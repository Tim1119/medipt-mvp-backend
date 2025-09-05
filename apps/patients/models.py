from django.db import models

# Create your models here.
from django.db import models
from apps.accounts.models import User
from shared.models import SoftDeleteModel, TimeStampedUUID
from django.core.validators import FileExtensionValidator
# from shared.validators import validate_blood_pressure
from cloudinary.models import CloudinaryField
from autoslug import AutoSlugField
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from django.utils.translation import gettext_lazy as _ 
from shared.validators import validate_phone_number,validate_blood_pressure
from shared.text_choices import BloodGroupChoices, Gender, GenotypeChoices,MaritalStatus
import uuid
from apps.organizations.models import Organization
from apps.caregivers.models import Caregiver
from cloudinary.models import CloudinaryField


class Patient(TimeStampedUUID,SoftDeleteModel):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE,db_index=True)
    first_name = models.CharField(max_length=255,verbose_name=_("Patient First Name"),db_index=True)
    last_name = models.CharField(max_length=255,verbose_name=_("Patient Last Name"),db_index=True)
    medical_id = models.CharField(max_length=30, unique=True,blank=True,null=True)
    date_of_birth = models.DateField(blank=True,null=True)
    marital_status = models.CharField(max_length=30,choices=MaritalStatus.choices,verbose_name=_("Patient Marital Status"),blank=True,null=True)
    profile_picture = CloudinaryField(
        'image',
        folder='patient_profile_pictures',
        default='default.png',
        allowed_formats=['jpg', 'png', 'jpeg'],
        transformation=[{'crop': 'limit', 'quality': 80}],
    )
    gender = models.CharField(max_length=20,choices=Gender.choices,blank=True,null=True)
    phone_number=models.CharField(max_length=15,validators=[validate_phone_number],blank=True,null=True)
    emergency_phone_number=models.CharField(max_length=15,validators=[validate_phone_number],blank=True,null=True)
    slug = AutoSlugField(populate_from='user', unique=True)
    address = models.TextField(verbose_name=_("Patient's Address"),blank=True,null=True)

    class Meta:
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['organization', 'last_name', 'first_name']),
        ]


    def save(self, *args, **kwargs):
        if not self.medical_id:
            self.medical_id = self.generate_unique_medical_id()
        super(Patient, self).save(*args, **kwargs)

    @property
    def profile_picture_url(self):
        try:
            url = self.profile_picture.url
        except:
            url ='' 
        return url

    def __str__(self):
        return f"Patient account for {self.first_name.title()} {self.last_name.title()}"
    
    def generate_unique_medical_id(self):
        acronym = self.organization.acronym.upper()  
        while True:
            unique_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
            medical_id = f"{acronym}_{unique_id}"
            if not Patient.objects.filter(medical_id=medical_id).exists():
                return medical_id
    
    @property
    def full_name(self):
        return self.last_name + ' ' + self.first_name 



class PatientMedicalRecord(TimeStampedUUID,SoftDeleteModel):

    patient = models.OneToOneField(Patient,on_delete=models.CASCADE,verbose_name=_("Patient"))
    blood_group = models.CharField(max_length=3, choices=BloodGroupChoices, help_text="Blood group of the patient",db_index=True)
    genotype = models.CharField(max_length=2, choices=GenotypeChoices, help_text="Genotype of the patient",db_index=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight of the patient in kilograms (kg)",blank=True, null=True)
    height = models.DecimalField(max_digits=4, decimal_places=1, help_text="Height of the patient in centimeters (cm)",blank=True, null=True)
    allergies = models.TextField(blank=True, null=True, help_text="Allergies (if any)")
    slug = AutoSlugField(populate_from='patient', unique=True)
    

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Patient Medical Record"
        verbose_name_plural = "Patient Medical Records"

class PatientDiagnosisDetails(TimeStampedUUID,SoftDeleteModel):
    patient = models.ForeignKey(Patient,on_delete=models.PROTECT,verbose_name=_("Patient"),db_index=True)
    organization = models.ForeignKey(Organization,on_delete=models.PROTECT,verbose_name=_("Organization"),db_index=True)
    caregiver= models.ForeignKey(Caregiver,on_delete=models.SET_NULL,verbose_name=_("Caregiver"),db_index=True)
    assessment = models.CharField(max_length=255,verbose_name=_("Assesssment"))
    diagnoses = models.CharField(max_length=255,verbose_name=_("Patient's Diagnoses"))
    medication = models.CharField(max_length=255,verbose_name=_("Medication"))
    health_allergies = models.TextField(blank=True, null=True, help_text="Health Allergies (if any)")
    health_care_center = models.CharField(max_length=255,verbose_name=_("Health Care Center"),db_index=True)
    slug = AutoSlugField(populate_from='patient', unique=True)
    notes=models.TextField()

    def __str__(self):
        return f"Patient Diagnosis Details {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Patient Diagnosis Details"
        verbose_name_plural = "Patient Diagnosis Details"


class VitalSign(TimeStampedUUID,SoftDeleteModel):
    patient_diagnoses_details = models.OneToOneField(PatientDiagnosisDetails,on_delete=models.CASCADE,verbose_name=_('Patient Diagnosis Details'),db_index=True)
    body_temperature = models.DecimalField(max_digits=4, decimal_places=1, help_text="Body temperature in degrees Celsius (°C)",blank=True, null=True)
    pulse_rate = models.PositiveIntegerField(help_text="Pulse rate in beats per minute (bpm)",blank=True, null=True)
    blood_pressure = models.CharField(max_length=7, validators=[validate_blood_pressure], help_text="Blood pressure in the format 'Systolic/Diastolic' (e.g., '120/80')",blank=True, null=True)
    blood_oxygen = models.DecimalField(max_digits=4, decimal_places=1, help_text="Blood oxygen level as a percentage (%)",blank=True, null=True)
    respiration_rate = models.PositiveIntegerField(help_text="Respiration rate in breaths per minute (bpm)",blank=True, null=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight of the patient in kilograms (kg)",blank=True, null=True)
    slug = AutoSlugField(populate_from='patient_diagnoses_details', unique=True)

    def __str__(self):
        return f"Vital Signs recorded on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vital Sign"
        verbose_name_plural = "Vital Signs"
