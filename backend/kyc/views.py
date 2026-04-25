from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, KYCSubmission, KYCDocument, Notification
from .serializers import UserSerializer, KYCSubmissionSerializer, KYCDocumentSerializer, NotificationSerializer
from django.core.exceptions import ValidationError
from django.db.models import Count, Avg, F
from django.utils import timezone
from datetime import timedelta
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'role': user.role,
                    'username': user.username
                })
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class KYCSubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = KYCSubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_reviewer():
            return KYCSubmission.objects.all().order_by('last_status_change_at')
        return KYCSubmission.objects.filter(merchant=user)

    def perform_create(self, serializer):
        # Check if submission already exists for this merchant
        if KYCSubmission.objects.filter(merchant=self.request.user).exists():
            raise ValidationError("KYC submission already exists for this merchant.")
        serializer.save(merchant=self.request.user)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        submission = self.get_object()
        if submission.merchant != request.user:
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        try:
            submission.transition_to('submitted')
            return Response({'status': 'submitted'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start_review(self, request, pk=None):
        if not request.user.is_reviewer():
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        submission = self.get_object()
        try:
            submission.transition_to('under_review')
            return Response({'status': 'under_review'})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def review_action(self, request, pk=None):
        if not request.user.is_reviewer():
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        
        submission = self.get_object()
        new_status = request.data.get('status')
        reason = request.data.get('reason', '')

        try:
            submission.transition_to(new_status, reason)
            return Response({'status': new_status})
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class KYCDocumentUploadView(generics.CreateAPIView):
    serializer_class = KYCDocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        submission, created = KYCSubmission.objects.get_or_create(merchant=self.request.user)
        serializer.save(submission=submission)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reviewer_metrics(request):
    if not request.user.is_reviewer():
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    last_7_days = timezone.now() - timedelta(days=7)
    
    queue_count = KYCSubmission.objects.filter(status='submitted').count()
    
    # Average time in queue for items that were submitted
    avg_time_in_queue = KYCSubmission.objects.filter(status='submitted').aggregate(
        avg_time=Avg(timezone.now() - F('last_status_change_at'))
    )['avg_time']

    # Approval rate over last 7 days
    total_reviewed = KYCSubmission.objects.filter(
        status__in=['approved', 'rejected'],
        last_status_change_at__gte=last_7_days
    ).count()
    
    approved_count = KYCSubmission.objects.filter(
        status='approved',
        last_status_change_at__gte=last_7_days
    ).count()

    approval_rate = (approved_count / total_reviewed * 100) if total_reviewed > 0 else 0

    return Response({
        'submissions_in_queue': queue_count,
        'avg_time_in_queue_seconds': avg_time_in_queue.total_seconds() if avg_time_in_queue else 0,
        'approval_rate_last_7_days': round(approval_rate, 2)
    })
