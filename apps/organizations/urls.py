from django.urls import path
from .views import (OrganizationDashboardView,OrganizationProfileView)


urlpatterns = [
   path('statistics/',OrganizationDashboardView.as_view(),name='organization-statistics'),
   path('profile/', OrganizationProfileView.as_view(), name='organization_profile'),
]


