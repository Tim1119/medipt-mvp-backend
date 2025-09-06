from rest_framework import serializers
from apps.accounts.models import User
from django.contrib.auth.password_validation import validate_password
from apps.patients.models import Patient
from django.db import IntegrityError, transaction
from shared.text_choices import UserRoles
from apps.patients.models import PatientMedicalRecord
from .models import Organization
from .organization_service import OrganizationService
from apps.patients.serializers import BasePatientSerializer
from apps.patients.mixins import PatientRepresentationMixin


class OrganizationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=True)
    organization_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ['id', 'name',  'logo', 'address', 'phone_number', 'slug', 'email','organization_logo_url']
        read_only_fields = ['id', 'slug']

    @transaction.atomic
    def update(self, instance, validated_data):
        email = validated_data.pop('email', None)

        if email and email != instance.user.email:
            if User.objects.filter(email=email).exists():
                raise serializers.ValidationError({"email": "This email is already in use."})
            instance.user.email = email
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
    def get_organization_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo and request:
            return request.build_absolute_uri(obj.logo.url)
        return None


class OrganizationRegisterPatientSerializer(PatientRepresentationMixin, BasePatientSerializer):
    """Serializer for organization staff to register new patients."""
    
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}, 
        validators=[validate_password]
    )

    class Meta(BasePatientSerializer.Meta):
        fields = BasePatientSerializer.Meta.fields + ['email', 'password']

    def create(self, validated_data):
        organization = self.context['request'].user.organization
        return OrganizationService.create_patient_for_organization(validated_data, organization)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation = self.add_user_fields_to_representation(instance, representation)
        representation = self.add_medical_record_to_representation(instance, representation)
        return representation


    