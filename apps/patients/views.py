from django.shortcuts import render
from apps.organizations.permissions import IsOrganization
from apps.caregivers.permissions import IsCaregiver
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from shared.mixins import OrganizationContextMixin
from .models import Patient,PatientDiagnosisDetails
from .serializers import PatientDetailSerializer,PatientDiagnosisSerializer
from rest_framework.response import Response
from django.db.models import Prefetch   
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


class PatientDiagnosisListView(OrganizationContextMixin,generics.ListAPIView):
    """
    List of patients with their latest diagnosis only
    """
    serializer_class = PatientDiagnosisSerializer
    permission_classes = [ IsAuthenticated & (IsOrganization | IsCaregiver)]

    def get_queryset(self):
        organization = self.get_organization()
        return (
            Patient.objects
            .prefetch_related(
                Prefetch(
                    'diagnoses',
                    queryset=PatientDiagnosisDetails.objects
                    .select_related('caregiver')
                    .order_by('-created_at')
                )
            )
            .filter(diagnoses__isnull=False,organization=organization)
            .distinct()
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['view_type'] = 'latest' 
        return context

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "success": True,
                "message": "Patients with latest diagnoses retrieved successfully",
                "data": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "success": True,
            "message": "Patients with latest diagnoses retrieved successfully",
            "data": serializer.data
        })
