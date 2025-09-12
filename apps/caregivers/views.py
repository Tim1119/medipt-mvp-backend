from amqp import NotFound
from django.shortcuts import render

from apps.patients.exceptions import PatientNotFoundException
from .models import Caregiver
from apps.patients.serializers import PatientProfileSerializer
from shared.mixins import OrganizationContextMixin
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.organizations.permissions import IsOrganization
from apps.caregivers.permissions import IsCaregiver,IsCaregiverSelf
from apps.patients.permissions import IsPatient


# Create your views here.
class CaregiverProfileView(OrganizationContextMixin, generics.RetrieveUpdateAPIView):
    """
    Retrieve or update patient info.
    - Org and Caregivers can view patients in their organization
    - Only the caregiver can update their own record
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, (IsOrganization | IsCaregiver ), IsCaregiverSelf]
    lookup_field = 'id'

    def get_queryset(self):
        organization = self.get_organization()
        return Caregiver.objects.filter(organization=organization)

    def get_object(self):
        try:
            return super().get_object()
        except NotFound:
            raise PatientNotFoundException()