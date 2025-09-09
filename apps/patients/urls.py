

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PatientRegistrationDetailsView,PatientDiagnosisListView,PatientDiagnosisHistoryView

urlpatterns = [
    path('patient-registration-details/<str:id>/', PatientRegistrationDetailsView.as_view(), name='patient-registration-details'),
    path('patients-diagnoses/', PatientDiagnosisListView.as_view(), name='patient-diagnosis-list'),
    path('patient-diagnoses-history/<str:id>/', PatientDiagnosisHistoryView.as_view(), name='patient-diagnosis-history'),
]


