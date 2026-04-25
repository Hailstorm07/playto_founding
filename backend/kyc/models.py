from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError
import json

class User(AbstractUser):
    ROLE_CHOICES = (
        ('merchant', 'Merchant'),
        ('reviewer', 'Reviewer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='merchant')

    def is_reviewer(self):
        return self.role == 'reviewer'

    def is_merchant(self):
        return self.role == 'merchant'

class KYCSubmission(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('more_info_requested', 'More Info Requested'),
    )

    merchant = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kyc_submission')
    assigned_reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Personal details
    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    # Business details
    business_name = models.CharField(max_length=255, blank=True)
    business_type = models.CharField(max_length=100, blank=True)
    expected_monthly_volume = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_status_change_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.merchant.username} - {self.status}"

    @property
    def is_at_risk(self):
        # Dynamic SLA tracking: Flag if in queue (submitted) for more than 24 hours
        if self.status == 'submitted':
            return (timezone.now() - self.last_status_change_at).total_seconds() > 86400
        return False

    def transition_to(self, new_status, reason=''):
        """
        State Machine Logic:
        - draft -> submitted
        - submitted -> under_review
        - under_review -> approved OR rejected OR more_info_requested
        - more_info_requested -> submitted
        """
        valid_transitions = {
            'draft': ['submitted'],
            'submitted': ['under_review'],
            'under_review': ['approved', 'rejected', 'more_info_requested'],
            'more_info_requested': ['submitted'],
            'approved': [],
            'rejected': [],
        }

        if new_status not in valid_transitions.get(self.status, []):
            raise ValidationError(f"Illegal state transition from {self.status} to {new_status}")

        # Round-robin assignment when moving to 'submitted'
        if new_status == 'submitted' and not self.assigned_reviewer:
            self._assign_reviewer_round_robin()

        old_status = self.status
        self.status = new_status
        if reason:
            self.rejection_reason = reason
        self.last_status_change_at = timezone.now()
        self.save()

        # Log notification
        Notification.objects.create(
            merchant=self.merchant,
            event_type='status_change',
            payload=json.dumps({
                'old_status': old_status,
                'new_status': new_status,
                'reason': reason
            })
        )

    def _assign_reviewer_round_robin(self):
        """
        Assigns the next reviewer in a round-robin fashion.
        """
        reviewers = User.objects.filter(role='reviewer').order_by('id')
        if not reviewers.exists():
            return

        # Simple round-robin: Find who was assigned the last submitted/under_review item
        last_assignment = KYCSubmission.objects.filter(
            assigned_reviewer__isnull=False
        ).order_by('-last_status_change_at').first()

        if not last_assignment or not last_assignment.assigned_reviewer:
            self.assigned_reviewer = reviewers.first()
        else:
            # Find the index of the last assigned reviewer and pick the next one
            reviewer_ids = list(reviewers.values_list('id', flat=True))
            try:
                last_idx = reviewer_ids.index(last_assignment.assigned_reviewer.id)
                next_idx = (last_idx + 1) % len(reviewer_ids)
                self.assigned_reviewer = reviewers[next_idx]
            except ValueError:
                self.assigned_reviewer = reviewers.first()

class KYCDocument(models.Model):
    DOCUMENT_TYPES = (
        ('PAN', 'PAN Card'),
        ('AADHAAR', 'Aadhaar Card'),
        ('BANK_STATEMENT', 'Bank Statement'),
    )
    submission = models.ForeignKey(KYCSubmission, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='kyc_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.submission.merchant.username} - {self.document_type}"

class Notification(models.Model):
    merchant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    event_type = models.CharField(max_length=50)
    payload = models.TextField() # JSON string
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.merchant.username} - {self.event_type} - {self.timestamp}"
