from .models import Caregiver
from rest_framework import serializers


class CaregiverSerializer(serializers.ModelSerializer):
    active = serializers.BooleanField(source='user.is_active', read_only=True)
    verified = serializers.BooleanField(source='user.is_verified', read_only=True)

    class Meta:
        model = Caregiver
        fields = ['first_name','last_name','caregiver_type','date_of_birth','marital_status','profile_picture','gender',
                  'phone_number','address','slug','id','active','verified','created_at','updated_at','staff_number']
