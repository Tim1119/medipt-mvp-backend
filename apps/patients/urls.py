

from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import PatientRegistrationDetailsView,PatientDiagnosisListView,PatientDiagnosisHistoryView, PatientDiagnosisVitalSignViewSet,PatienProfileView
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register('patient-diagnoses-with-vital-sign', PatientDiagnosisVitalSignViewSet,basename='patient-diagnoses-with-vital-sign')


urlpatterns = [
    path('', include(router.urls)),
    path('patient-registration-details/<str:id>/', PatientRegistrationDetailsView.as_view(), name='patient-registration-details'),
    path('patients-diagnoses/', PatientDiagnosisListView.as_view(), name='patient-diagnosis-list'),
    path('patient-diagnoses-history/<str:id>/', PatientDiagnosisHistoryView.as_view(), name='patient-diagnosis-history'),
    path('patient-profile-view/<str:id>/',PatienProfileView.as_view(), name='patient-profile-view'),
]


