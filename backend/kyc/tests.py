from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import User, KYCSubmission

class KYCStateMachineTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_merchant', role='merchant')
        self.submission = KYCSubmission.objects.create(merchant=self.user, status='draft')

    def test_valid_transition(self):
        # draft -> submitted (Valid)
        self.submission.transition_to('submitted')
        self.assertEqual(self.submission.status, 'submitted')

    def test_invalid_transition(self):
        # draft -> approved (Invalid)
        with self.assertRaises(ValidationError):
            self.submission.transition_to('approved')
        self.assertEqual(self.submission.status, 'draft')

    def test_illegal_approved_to_draft(self):
        # approved -> draft (Invalid)
        self.submission.status = 'approved'
        self.submission.save()
        
        with self.assertRaises(ValidationError):
            self.submission.transition_to('draft')
        self.assertEqual(self.submission.status, 'approved')

    def test_reviewer_workflow(self):
        # draft -> submitted
        self.submission.transition_to('submitted')
        
        # submitted -> under_review
        self.submission.transition_to('under_review')
        
        # under_review -> approved
        self.submission.transition_to('approved')
        self.assertEqual(self.submission.status, 'approved')

    def test_round_robin_assignment(self):
        # Create multiple reviewers
        reviewer1 = User.objects.create_user(username='rev1', role='reviewer')
        reviewer2 = User.objects.create_user(username='rev2', role='reviewer')
        
        # Submission 1 -> should go to rev1 (first by ID)
        sub1 = KYCSubmission.objects.create(merchant=User.objects.create_user(username='m1', role='merchant'))
        sub1.transition_to('submitted')
        self.assertEqual(sub1.assigned_reviewer, reviewer1)
        
        # Submission 2 -> should go to rev2
        sub2 = KYCSubmission.objects.create(merchant=User.objects.create_user(username='m2', role='merchant'))
        sub2.transition_to('submitted')
        self.assertEqual(sub2.assigned_reviewer, reviewer2)
        
        # Submission 3 -> should go back to rev1
        sub3 = KYCSubmission.objects.create(merchant=User.objects.create_user(username='m3', role='merchant'))
        sub3.transition_to('submitted')
        self.assertEqual(sub3.assigned_reviewer, reviewer1)
