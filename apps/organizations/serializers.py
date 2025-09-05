from rest_framework import serializers
from apps.accounts.models import User
from django.contrib.auth.password_validation import validate_password
from apps.patients.models import Patient
from django.db import IntegrityError, transaction
from shared.text_choices import UserRoles
from apps.patients.models import PatientMedicalRecord
from .models import Organization


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

    