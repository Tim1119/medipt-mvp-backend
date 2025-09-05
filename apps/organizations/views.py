from django.shortcuts import get_object_or_404
from django.db.models import Count, Q,Sum
from apps.patients.models import Patient
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Organization
from .permissions import IsOrganization, IsOrganizationWithAccount
from apps.caregivers.models import Caregiver
from rest_framework.exceptions import NotFound
from rest_framework import generics
from .serializers import OrganizationSerializer

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