from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (LatestPatientsView, OrganizationDashboardView,OrganizationProfileView,PatientViewSet, RegisterPatientView,CaregiverViewSet,LatestCaregiverView)


router = DefaultRouter()
router.register('all-patients',PatientViewSet, basename='patients')
router.register('all-caregivers',CaregiverViewSet, basename='caregivers')

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/',OrganizationDashboardView.as_view(),name='organization-statistics'),
    path('profile/', OrganizationProfileView.as_view(), name='organization_profile'),
    
    path('latest-patients/', LatestPatientsView.as_view(),name='latest-patients'),
    path('register-new-patient/', RegisterPatientView.as_view(), name='register-new-patient'),
    
    path('latest-caregivers/', LatestCaregiverView.as_view(),name='latest-caregivers'),
]


