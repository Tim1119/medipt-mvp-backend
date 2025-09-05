# management/commands/seed_db.py
from django.core.management.base import BaseCommand
from faker import Faker
import random
from apps.accounts.models import User
from apps.organizations.models import Organization
from apps.caregivers.models import Caregiver, role_abbreviation
from apps.patients.models import Patient, PatientMedicalRecord, PatientDiagnosisDetails, VitalSign
from medipt.apps.accounts.user_roles import UserRoles
from shared.text_choices import Gender, MaritalStatus, BloodGroupChoices, GenotypeChoices
from datetime import date

fake = Faker()

class Command(BaseCommand):
    help = "Seed the database with test data"

    def add_arguments(self, parser):
        parser.add_argument('--orgs', type=int, default=5, help='Number of organizations')
        parser.add_argument('--caregivers', type=int, default=50, help='Number of caregivers per organization')
        parser.add_argument('--patients', type=int, default=200, help='Number of patients per organization')

    def handle(self, *args, **options):
        org_count = options['orgs']
        caregivers_per_org = options['caregivers']
        patients_per_org = options['patients']

        organizations = []
        all_caregivers = []

        # Create organizations
        for _ in range(org_count):
            user = User.objects.create_user(
                email=fake.unique.email(),
                password="password2000",
                role=UserRoles.ORGANIZATION,
                is_active=True,
                is_verified=True
            )
            org = Organization.objects.create(
                user=user,
                name=fake.company(),
                acronym=fake.unique.lexify(text='???').upper(),
                address=fake.address(),
                phone_number=fake.phone_number(),
            )
            organizations.append(org)

        # Create caregivers
        for org in organizations:
            org_caregivers = []
            for _ in range(caregivers_per_org):
                user = User.objects.create_user(
                    email=fake.unique.email(),
                    password="password2000",
                    role=UserRoles.CAREGIVER,
                    is_active=True,
                    is_verified=True
                )
                caregiver_type = random.choice(list(role_abbreviation.keys()))
                caregiver = Caregiver.objects.create(
                    user=user,
                    organization=org,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    caregiver_type=caregiver_type,
                    gender=random.choice([Gender.MALE, Gender.FEMALE]),
                    date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=60),
                    marital_status=random.choice(list(MaritalStatus.choices)),
                    phone_number=fake.phone_number(),
                )
                org_caregivers.append(caregiver)
                all_caregivers.append(caregiver)

            org.caregivers = org_caregivers  # optional for reference

        # Create patients
        for org in organizations:
            for _ in range(patients_per_org):
                user = User.objects.create_user(
                    email=fake.unique.email(),
                    password="password2000",
                    role=UserRoles.PATIENT,
                    is_active=True,
                    is_verified=True
                )
                patient = Patient.objects.create(
                    user=user,
                    organization=org,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    gender=random.choice([Gender.MALE, Gender.FEMALE]),
                    date_of_birth=fake.date_of_birth(minimum_age=0, maximum_age=90),
                    marital_status=random.choice(list(MaritalStatus.choices)),
                    phone_number=fake.phone_number(),
                    emergency_phone_number=fake.phone_number(),
                )

                # Medical record
                PatientMedicalRecord.objects.create(
                    patient=patient,
                    blood_group=random.choice(list(BloodGroupChoices.choices)),
                    genotype=random.choice(list(GenotypeChoices.choices)),
                    weight=random.randint(40, 120),
                    height=random.randint(140, 200),
                )

                # Diagnosis (assign caregiver from same org)
                diag = PatientDiagnosisDetails.objects.create(
                    patient=patient,
                    organization=org,
                    caregiver=random.choice([c for c in all_caregivers if c.organization == org]),
                    assessment=fake.sentence(),
                    diagnoses=fake.word(),
                    medication=fake.word(),
                    health_care_center=fake.company(),
                    notes=fake.text(),
                )

                # Vital signs
                VitalSign.objects.create(
                    patient_diagnoses_details=diag,
                    body_temperature=round(random.uniform(36.0, 39.0), 1),
                    pulse_rate=random.randint(60, 120),
                    blood_pressure=f"{random.randint(100, 140)}/{random.randint(60, 90)}",
                    blood_oxygen=round(random.uniform(90.0, 100.0), 1),
                    respiration_rate=random.randint(12, 24),
                    weight=random.randint(40, 120),
                )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {org_count} organizations, '
            f'{len(all_caregivers)} caregivers, and '
            f'{patients_per_org * org_count} patients.'
        ))
