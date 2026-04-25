import os
import django
import json
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playto_pay.settings')
django.setup()

from kyc.models import User, KYCSubmission, KYCDocument, Notification
from rest_framework.authtoken.models import Token

def seed():
    print("Seeding database...")
    
    # Create Reviewer
    reviewer, created = User.objects.get_or_create(
        username='reviewer1',
        email='reviewer@playto.com',
        role='reviewer'
    )
    if created:
        reviewer.set_password('password123')
        reviewer.save()
        Token.objects.get_or_create(user=reviewer)
        print("Created reviewer: reviewer1 / password123")

    # Create Reviewer 2
    reviewer2, created = User.objects.get_or_create(
        username='reviewer2',
        email='reviewer2@playto.com',
        role='reviewer'
    )
    if created:
        reviewer2.set_password('password123')
        reviewer2.save()
        Token.objects.get_or_create(user=reviewer2)
        print("Created reviewer: reviewer2 / password123")

    # Merchant 1: Draft
    m1, created = User.objects.get_or_create(
        username='merchant_draft',
        email='m1@playto.com',
        role='merchant'
    )
    if created:
        m1.set_password('password123')
        m1.save()
        Token.objects.get_or_create(user=m1)
        KYCSubmission.objects.create(
            merchant=m1,
            status='draft',
            full_name='John Draft',
            business_name='Draft Ventures'
        )
        print("Created merchant: merchant_draft / password123 (Status: Draft)")

    # Merchant 2: Under Review
    m2, created = User.objects.get_or_create(
        username='merchant_review',
        email='m2@playto.com',
        role='merchant'
    )
    if created:
        m2.set_password('password123')
        m2.save()
        Token.objects.get_or_create(user=m2)
        sub = KYCSubmission.objects.create(
            merchant=m2,
            assigned_reviewer=reviewer,
            status='under_review',
            full_name='Alice Review',
            email='alice@review.com',
            phone='+91 98765 43210',
            business_name='Review Corp',
            business_type='proprietorship',
            expected_monthly_volume=5000,
            last_status_change_at=timezone.now() - timedelta(hours=25) # Flag as at_risk
        )
        print("Created merchant: merchant_review / password123 (Status: Under Review, At Risk)")

    # Merchant 3: Submitted (for queue testing)
    m3, created = User.objects.get_or_create(
        username='merchant_submitted',
        email='m3@playto.com',
        role='merchant'
    )
    if created:
        m3.set_password('password123')
        m3.save()
        Token.objects.get_or_create(user=m3)
        KYCSubmission.objects.create(
            merchant=m3,
            assigned_reviewer=reviewer2,
            status='submitted',
            full_name='Bob Sub',
            email='m3@playto.com',
            phone='+91 99999 88888',
            business_name='Sub Systems',
            business_type='individual',
            expected_monthly_volume=2000,
            last_status_change_at=timezone.now() - timedelta(hours=10)
        )
        print("Created merchant: merchant_submitted / password123 (Status: Submitted)")

    print("Seeding completed.")

if __name__ == '__main__':
    seed()
