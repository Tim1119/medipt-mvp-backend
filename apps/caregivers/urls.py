
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CaregiverProfileView
from rest_framework.routers import DefaultRouter




urlpatterns = [
   
    path('caregiver-profile-view/<str:id>/',CaregiverProfileView.as_view(), name='caregiver-profile-view'),
]
