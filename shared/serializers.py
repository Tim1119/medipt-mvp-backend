import logging

from rest_framework import serializers
from rest_framework.fields import empty

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from shared.exceptions import ValidationException

logger = logging.getLogger(__name__)


class BaseModelSerializer(serializers.ModelSerializer):
    """Enhanced base serializer with common functionality"""

    # Common read-only fields
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        # Extract user from context for permission checks
        self.user = kwargs.pop("user", None)
        if not self.user and "context" in kwargs:
            request = kwargs["context"].get("request")
            if request and hasattr(request, "user"):
                self.user = request.user
        super().__init__(instance, data, **kwargs)

    def validate(self, attrs):
        """Enhanced validation with better error handling"""
        try:
            attrs = super().validate(attrs)

            # Add common validation logic
            if hasattr(self.Meta.model, "clean"):
                # Create a temporary instance for model validation
                if self.instance:
                    temp_instance = self.instance
                    for attr, value in attrs.items():
                        setattr(temp_instance, attr, value)
                else:
                    temp_instance = self.Meta.model(**attrs)

                try:
                    temp_instance.clean()
                except DjangoValidationError as e:
                    raise ValidationException(detail=str(e))

            return attrs
        except serializers.ValidationError as e:
            logger.warning(f"Validation error in {self.__class__.__name__}: {e}")
            raise

    def create(self, validated_data):
        """Enhanced create with transaction and logging"""
        try:
            with transaction.atomic():
                # Auto-assign organization if applicable
                if (
                    self.user
                    and hasattr(self.user, "get_organization")
                    and hasattr(self.Meta.model, "organization")
                    and "organization" not in validated_data
                ):
                    organization = self.user.get_organization()
                    if organization:
                        validated_data["organization"] = organization

                instance = super().create(validated_data)
                logger.info(
                    f"Created {self.Meta.model.__name__} with ID: {instance.id}"
                )
                return instance
        except Exception as e:
            logger.error(f"Error creating {self.Meta.model.__name__}: {e}")
            raise ValidationException(
                detail=f"Failed to create {self.Meta.model.__name__}: {str(e)}"
            )

    def update(self, instance, validated_data):
        """Enhanced update with transaction and logging"""
        try:
            with transaction.atomic():
                instance = super().update(instance, validated_data)
                logger.info(
                    f"Updated {self.Meta.model.__name__} with ID: {instance.id}"
                )
                return instance
        except Exception as e:
            logger.error(f"Error updating {self.Meta.model.__name__}: {e}")
            raise ValidationException(
                detail=f"Failed to update {self.Meta.model.__name__}: {str(e)}"
            )
