from django.shortcuts import render
from apps.organizations.permissions import IsOrganization
from apps.caregivers.permissions import IsCaregiver
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from shared.mixins import OrganizationContextMixin
from .models import Patient
from .serializers import PatientDetailSerializer
# Create your views here.


class PatientRegistrationDetailsView(OrganizationContextMixin,generics.RetrieveUpdateAPIView):
    """
    Retrieve detailed information for a specific patient by id.
    Accessible to authenticated organization or caregiver users.
    Returns patient details including medical record and user-related fields.
    """
    serializer_class = PatientDetailSerializer
    permission_classes = [ IsAuthenticated & (IsOrganization | IsCaregiver)]
    lookup_field = 'id'

    def get_queryset(self):
        organization = self.get_organization()
        return Patient.objects.filter(organization=organization).select_related('user').prefetch_related('patientmedicalrecord')

