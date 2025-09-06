from django.shortcuts import get_object_or_404
from django.db.models import Count, Q,Sum
from apps.patients.models import Patient
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView,RetrieveAPIView,ListAPIView,CreateAPIView
from apps.organizations.mixins import OrganizationContextMixin
from apps.patients.serializers import PatientSerializer
from .models import Organization
from .permissions import IsOrganization, IsOrganizationWithAccount
from apps.caregivers.models import Caregiver
from rest_framework.exceptions import NotFound
from rest_framework import generics
from .serializers import OrganizationRegisterPatientSerializer, OrganizationSerializer
from apps.caregivers.permissions import IsCaregiver
from shared.text_choices import UserRoles
from shared.pagination import StandardResultsSetPagination
from rest_framework.mixins import RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin,ListModelMixin
from rest_framework import viewsets
from rest_framework.decorators import action


#james65@example.com

class OrganizationDashboardView(APIView):
    """
    Retrieves organization statistics and latest 10 caregivers and patient for the dashboard.
    """
    permission_classes = [IsAuthenticated, IsOrganizationWithAccount]

    def get(self, request, *args, **kwargs):

        organization = request.user.organization

        caregiver_stats = Caregiver.objects.filter(organization=organization).aggregate(
            total=Count("pkid"),
            active=Count("pkid", filter=Q(user__is_active=True)),
            verified=Count("pkid", filter=Q(user__is_verified=True)),
        )

        patient_stats = Patient.objects.filter(organization=organization).aggregate(
            total=Count("pkid"),
            active=Count("pkid", filter=Q(user__is_active=True)),
            verified=Count("pkid", filter=Q(user__is_verified=True)),
            active_male=Count("pkid", filter=Q(user__is_active=True, gender="Male")),
            active_female=Count("pkid", filter=Q(user__is_active=True, gender="Female")),
            verified_male=Count("pkid", filter=Q(user__is_verified=True, gender="Male")),
            verified_female=Count("pkid", filter=Q(user__is_verified=True, gender="Female")),
        )

        response_data = {
            "statistics": {
                "caregivers": caregiver_stats,
                "patients": patient_stats,
            },
        }

        return Response({"message": "Organization Dashboard Data", "data": response_data}, status=status.HTTP_200_OK)


class OrganizationProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the profile of the logged-in organization.
    """
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated, IsOrganization]

    def get_object(self):
        try:
            return Organization.objects.get(user=self.request.user)
        except Organization.DoesNotExist:
            raise NotFound("Organization not found for this user")
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"message": "Organization profile retrieved successfully","data": serializer.data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Organization profile updated successfully","data": serializer.data})
    

class LatestPatientsView(OrganizationContextMixin, ListAPIView):
    permission_classes = [IsAuthenticated, IsOrganization | IsCaregiver]
    serializer_class = PatientSerializer

    def get_queryset(self):
        organization = self.get_organization()
        return Patient.objects.filter(
            organization=organization,
            user__is_verified=True,
            user__is_active=True,
            user__role=UserRoles.PATIENT
        )[:5]
    
class PatientViewSet(OrganizationContextMixin,ListModelMixin,RetrieveModelMixin,UpdateModelMixin,DestroyModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, IsOrganization | IsCaregiver]
    serializer_class = PatientSerializer
    search_fields = ['first_name', 'last_name', 'medical_id']
    filterset_fields = ['medical_id', 'user__is_active']
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        organization = self.get_organization()
        return Patient.objects.filter(
                organization=organization,
                user__is_verified=True,
                user__is_active=True,
                user__role=UserRoles.PATIENT
            )
    
    @action(detail=True, methods=['patch'], url_path='toggle-status')
    def toggle_status(self, request, slug=None):
        """
        Toggle the patient's active status
        """
        patient = Patient.objects.filter(slug=slug,organization=self.get_organization()).first()
        patient.user.is_active = not patient.user.is_active
        patient.user.is_verified = not patient.user.is_verified
        patient.user.save()
        serializer = self.get_serializer(patient)
        return Response({"message": "Patient status toggled {} successfully".format("off" if patient.user.is_active else "on"), "data": serializer.data},status=status.HTTP_200_OK)
    

class RegisterPatientView(CreateAPIView):

    """
    Creates a new patient associated with the authenticated organization and send a notification
    to the user notifying them that an account has been created for them
    """ 

    serializer_class = OrganizationRegisterPatientSerializer
    permission_classes = [IsAuthenticated, IsOrganizationWithAccount]

    def perform_create(self, serializer):
        serializer.save()