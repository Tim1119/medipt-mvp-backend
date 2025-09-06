from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (LatestPatientsView, OrganizationDashboardView,OrganizationProfileView,PatientViewSet)


router = DefaultRouter()
router.register('all-patients',PatientViewSet, basename='patient')

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/',OrganizationDashboardView.as_view(),name='organization-statistics'),
    path('profile/', OrganizationProfileView.as_view(), name='organization_profile'),
    
    path('latest-patients/', LatestPatientsView.as_view(),name='latest-patients'),
]


