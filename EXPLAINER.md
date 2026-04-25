# AI Explainer

### 1. The State Machine
The state machine lives in the `KYCSubmission` model in `backend/kyc/models.py`.

```python
def transition_to(self, new_status, reason=''):
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
    # ... update status and log notification
```

Illegal transitions are prevented by checking the `valid_transitions` dictionary. If a transition is not defined, a `ValidationError` is raised, which the API layer catches and returns as a 400 Bad Request.

### 2. The Upload
File uploads are validated in the `KYCDocumentSerializer` in `backend/kyc/serializers.py`.

```python
def validate_file(self, value):
    # Validate file size (max 5 MB)
    if value.size > 5 * 1024 * 1024:
        raise serializers.ValidationError("File size must be less than 5 MB.")

    # Validate file type (PDF, JPG, PNG)
    ext = value.name.split('.')[-1].lower()
    if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
        raise serializers.ValidationError("Only PDF, JPG, and PNG files are allowed.")
    
    return value
```

If someone sends a 50 MB file, the `value.size > 5 * 1024 * 1024` check will fail, and a clear error message will be returned to the client.

### 3. The Queue
The query that powers the reviewer dashboard list and SLA flag is in `KYCSubmissionViewSet.get_queryset` and the `is_at_risk` property.

```python
# Query for the queue (ordered by oldest change first)
def get_queryset(self):
    user = self.request.user
    if user.is_reviewer():
        return KYCSubmission.objects.all().order_by('last_status_change_at')
    return KYCSubmission.objects.filter(merchant=user)

# SLA Flag (Dynamic)
@property
def is_at_risk(self):
    if self.status == 'submitted':
        return (timezone.now() - self.last_status_change_at).total_seconds() > 86400
    return False
```

I wrote it this way to ensure the SLA status is computed dynamically on each request, as requested. Storing a flag would lead to stale data. Ordering by `last_status_change_at` ensures the reviewer sees the oldest items first.

### 4. The Auth
Merchant isolation is handled in `KYCSubmissionViewSet.get_queryset`.

```python
def get_queryset(self):
    user = self.request.user
    if user.is_reviewer():
        return KYCSubmission.objects.all()
    return KYCSubmission.objects.filter(merchant=user)
```

This ensures that a merchant can only ever retrieve their own submission. Additionally, the `submit` action checks `if submission.merchant != request.user` to prevent cross-user submissions.

### 5. The AI Audit
Example where AI gave buggy code:
AI suggested using `DateTimeField(auto_now=True)` for `last_status_change_at`. 

**Bug**: `auto_now=True` updates the field on *every* save, not just when the status changes. If a merchant updates their business name while in `draft`, the `last_status_change_at` would reset, incorrectly affecting the SLA calculation.

**Replacement**: I replaced it with a manual update inside the `transition_to` method:
```python
self.status = new_status
self.last_status_change_at = timezone.now() # Only updates on explicit transition
self.save()
```
