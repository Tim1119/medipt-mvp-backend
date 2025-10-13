from amqp import NotFound
from django.shortcuts import get_object_or_404, render
from apps.organizations.permissions import IsOrganization
from apps.caregivers.permissions import IsCaregiver
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from apps.caregivers.models import Caregiver
from apps.patients.exceptions import PatientNotFoundException
from apps.patients.permission import IsPatient,IsPatientSelf
from shared.mixins import OrganizationContextMixin
from .models import Patient,PatientDiagnosisDetails
from .serializers import PatientDetailSerializer,PatientDiagnosisSerializer,PatientDiagnosisWithVitalSignSerializer, PatientProfileSerializer
from rest_framework.response import Response
from django.db.models import Prefetch   
from django.db.models import Q
from rest_framework import status
from rest_framework.validators import ValidationError
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

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
    # parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        organization = self.get_organization()
        return Patient.objects.filter(organization=organization,deleted_at__isnull=True).select_related('user').prefetch_related('patientmedicalrecord')


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
            .filter(diagnoses__isnull=False,organization=organization,deleted_at__isnull=True)
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
            PatientDiagnosisDetails.objects.filter(patient=patient,deleted_at__isnull=True)
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



class PatientDiagnosisVitalSignViewSet(OrganizationContextMixin, viewsets.ModelViewSet):
    """
    Handles creation, update, retrieval of patient diagnoses with vital signs.
    
    - Caregivers: create/update for their own patients; caregiver is auto-assigned.
    - Organization users: can select caregiver from organization.
    """

    serializer_class = PatientDiagnosisWithVitalSignSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        organization = self.get_organization()
        return PatientDiagnosisDetails.objects.filter(
            organization=organization, 
            deleted_at__isnull=True
        ).select_related(
            'patient', 'caregiver', 'organization'
        ).prefetch_related('vitalsign')

    def perform_create(self, serializer):
        organization = self.get_organization()

        # Get patient from validated data (note: source='patient' means the key is 'patient')
        patient_id = serializer.validated_data.get('patient')
        if not patient_id:
            raise ValidationError("Patient ID is required")
        
        patient = get_object_or_404(Patient, id=patient_id, organization=organization)

        # Determine caregiver
        if hasattr(self.request.user, 'caregiver'):
            caregiver = self.request.user.caregiver
        else:
            caregiver_id = serializer.validated_data.get('caregiver') or self.request.data.get('caregiver')
            if not caregiver_id:
                raise ValidationError("Caregiver is required for organization users")
            caregiver = get_object_or_404(Caregiver, id=caregiver_id, organization=organization)

        # Save with context - let serializer and service handle the rest
        serializer.save(
            organization=organization,
            patient=patient,
            caregiver=caregiver
        )

    def create(self, request, *args, **kwargs):
        organization = self.get_organization()
        serializer = self.get_serializer(
            data=request.data, 
            context={'request': request, 'organization': organization}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "success": True,
            "message": "Patient diagnosis and vital signs created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        organization = self.get_organization()
        
        serializer = self.get_serializer(
            instance, 
            data=request.data, 
            partial=True, 
            context={'request': request, 'organization': organization}
        )
        serializer.is_valid(raise_exception=True)

        # Determine caregiver for update
        if hasattr(self.request.user, 'caregiver'):
            caregiver = self.request.user.caregiver
        else:
            caregiver_id = request.data.get('caregiver')
            caregiver = instance.caregiver  # fallback to existing
            if caregiver_id:
                caregiver = get_object_or_404(Caregiver, id=caregiver_id, organization=organization)

        # Patient cannot change in update
        patient = instance.patient

        serializer.save(
            organization=organization,
            patient=patient,
            caregiver=caregiver
        )
        
        return Response({
            "success": True,
            "message": "Patient diagnosis and vital signs updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    

class PatienProfileView(OrganizationContextMixin, generics.RetrieveUpdateAPIView):
    """
    Retrieve or update patient info.
    - Org and Caregivers can view patients in their organization
    - Patients can view themselves
    - Only the patient can update their own record
    """
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, (IsOrganization | IsCaregiver | IsPatient), IsPatientSelf]
    lookup_field = 'id'
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        organization = self.get_organization()
        return Patient.objects.filter(organization=organization)

    def get_object(self):
        try:
            return super().get_object()
        except NotFound:
            raise PatientNotFoundException()


