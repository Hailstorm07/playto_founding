from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SignupView, LoginView, KYCSubmissionViewSet, 
    KYCDocumentUploadView, reviewer_metrics
)

router = DefaultRouter()
router.register(r'submissions', KYCSubmissionViewSet, basename='submission')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('documents/', KYCDocumentUploadView.as_view(), name='document-upload'),
    path('metrics/', reviewer_metrics, name='reviewer-metrics'),
    path('', include(router.urls)),
]
