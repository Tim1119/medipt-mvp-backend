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
from django.db.models import Q
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


class PatientDiagnosisHistoryView(OrganizationContextMixin, generics.RetrieveAPIView):
    """
    Get  a patient details with all their diagnoses history
    """

    serializer_class = PatientDiagnosisSerializer
    permission_classes = [IsAuthenticated & (IsOrganization | IsCaregiver)]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    def get_queryset(self):
        organization = self.get_organization()
        return Patient.objects.filter(organization=organization)

    def get_diagnoses_queryset(self, patient):
        qs = (
            PatientDiagnosisDetails.objects.filter(patient=patient)
            .select_related("caregiver", "patient", "organization")
            .prefetch_related("vitalsign")
        )

        # Apply search
        search_query = self.request.GET.get("search")
        if search_query:
            qs = qs.filter(
                Q(assessment__icontains=search_query)
                | Q(diagnoses__icontains=search_query)
                | Q(medication__icontains=search_query)
            )

        # Apply ordering (defaults to -created_at)
        ordering = self.request.GET.get("ordering", "-created_at")
        return qs.order_by(ordering)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        patient = self.get_object()  # DRF handles lookup by medical_id here
        context["diagnoses_queryset"] = self.get_diagnoses_queryset(patient)
        return context

    def retrieve(self, request, *args, **kwargs):
        patient = self.get_object()  # DRF resolves this
        serializer = self.get_serializer(patient)
        return Response(
            {
                "success": True,
                "message": "Patient diagnosis history retrieved successfully",
                "data": serializer.data,
            }
        )
