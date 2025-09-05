from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from shared.validators import validate_organization_acronym
from rest_framework import serializers
from .user_roles import UserRoles
from apps.organizations.models import Organization, User  
import logging
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed



from rest_framework import serializers
from apps.organizations.models import Organization, User
from shared.validators import validate_organization_acronym
from apps.organizations.organization_service import OrganizationService

class OrganizationSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    acronym = serializers.CharField(max_length=10, min_length=2, validators=[validate_organization_acronym])
    role = serializers.ChoiceField(choices=UserRoles.choices, default=UserRoles.ORGANIZATION)
    user_email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'acronym', 'email' ,'role','user_email','password']
        read_only_fields = ['id', 'user_email']

    def get_user_email(self, obj):
        return obj.user.email

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
       
    def validate_acronym(self, value):
        if Organization.objects.filter(acronym=value).exists():
            raise serializers.ValidationError("An organization with this acronym already exists.")
        return value
       
    def create(self, validated_data):
        return OrganizationService.create_organization(
            name=validated_data['name'],
            acronym=validated_data['acronym'],
            email=validated_data['email'],
            password=validated_data['password']
        )


class ResendActivationLinkSerializer(serializers.Serializer):
    '''This serillizer is used by users to request new activation link'''
    email = serializers.EmailField()



class LoginSerializer(serializers.Serializer):
    '''This serillizer is used by users to login'''

    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    id = serializers.UUIDField(read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailed("Your account is not yet activated. Please check your email.")

        if not user.is_verified:
            raise AuthenticationFailed("Your account is not verified. Please check your email.")

        # Generate JWT tokens using SimpleJWT
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return {
            "user":user,
            "refresh_token": str(refresh),
            "access_token": str(access),
        }

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
