from rest_framework import serializers
from .models import User, KYCSubmission, KYCDocument, Notification
from django.core.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ('id', 'document_type', 'file', 'uploaded_at')

    def validate_file(self, value):
        # Validate file size (max 5 MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 5 MB.")

        # Validate file type (PDF, JPG, PNG)
        ext = value.name.split('.')[-1].lower()
        if ext not in ['pdf', 'jpg', 'jpeg', 'png']:
            raise serializers.ValidationError("Only PDF, JPG, and PNG files are allowed.")
        
        return value

class KYCSubmissionSerializer(serializers.ModelSerializer):
    documents = KYCDocumentSerializer(many=True, read_only=True)
    merchant_name = serializers.CharField(source='merchant.username', read_only=True)
    assigned_reviewer_name = serializers.CharField(source='assigned_reviewer.username', read_only=True)
    is_at_risk = serializers.BooleanField(read_only=True)

    class Meta:
        model = KYCSubmission
        fields = (
            'id', 'merchant_name', 'assigned_reviewer_name', 'status', 'full_name', 'email', 'phone',
            'business_name', 'business_type', 'expected_monthly_volume',
            'rejection_reason', 'created_at', 'updated_at', 'documents', 'is_at_risk'
        )
        read_only_fields = ('status', 'rejection_reason', 'created_at', 'updated_at')

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
