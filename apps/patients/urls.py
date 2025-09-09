

from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import PatientRegistrationDetailsView

urlpatterns = [
    path('patient-registration-details/<str:id>/', PatientRegistrationDetailsView.as_view(), name='patient-registration-details'),
]


