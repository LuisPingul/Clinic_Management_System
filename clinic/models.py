from django.db import models
from django.utils import timezone

# ---------------------------------------------------------
# 1. DOCTOR TABLE
# ---------------------------------------------------------
class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialty = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10)
    # A simple text field where the doctor can write: "Mon-Fri, 9AM-5PM"
    availability_schedule = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.name}"

# ---------------------------------------------------------
# 2. PATIENT TABLE (Managed strictly by Nurse)
# ---------------------------------------------------------
class Patient(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField()
    date_registered = models.DateTimeField(default=timezone.now) 

    
    SEX_CHOICES = [
        ('Male','Male'),
        ('Female','Female'),
        ('Other','Other'),
    ]
    BLOOD_TYPE_CHOICES = [
        ('Unknown', 'Leave as null / Unknown'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    sex = models.CharField(max_length=10, choices=SEX_CHOICES, blank=True, null=True)
    height = models.IntegerField(help_text="Height in cm", blank=True, null=True)
    weight = models.IntegerField(help_text="Weight in kg", blank=True, null=True)
    blood_type = models.CharField(max_length=10, choices=BLOOD_TYPE_CHOICES, default='Unknown')

    comorbidities = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
# ---------------------------------------------------------
# 3. APPOINTMENT & QUEUE TABLE
# ---------------------------------------------------------
class Appointment(models.Model):
    # These are the Status Choices the Nurse uses to manage the physical clinic flow
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('WAITING', 'Waiting in Lobby'),
        ('LATE', 'Late'),
        ('IN_CONSULTATION', 'In Consultation'),
        ('CLEARED', 'Cleared / Paid'),
        ('NO_SHOW', 'No-Show'),
    ]

    # Linking the Patient and the Doctor
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    
    # Scheduling Details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    # Feature: Differentiate between scheduled and walk-in patients
    is_walk_in = models.BooleanField(default=False)
    
    # The current status managed by the Nurse
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')

    # -----------------------------------------------------
    # CLINICAL DATA (Inputted strictly by the Doctor)
    # -----------------------------------------------------
    symptoms = models.TextField(blank=True, null=True, help_text="Patient's reported issues")
    doctor_diagnosis = models.TextField(blank=True, null=True)
    doctor_recommendation = models.TextField(blank=True, null=True, help_text="Specific notes for the patient")
    prescription_details = models.TextField(blank=True, null=True, help_text="Medicines to be converted to PDF later")

    def __str__(self):
        return f"{self.patient} with {self.doctor} on {self.appointment_date}"


# ---------------------------------------------------------
# 4. PRESCRIPTION ITEM TABLE
# ---------------------------------------------------------
class PrescriptionItem(models.Model):
    FORM_CHOICES = [
        ('Tablet', 'Tablet(s)'),
        ('Capsule', 'Capsule(s)'),
        ('Tbsp', 'Tablespoon(s)'),
        ('Tsp', 'Teaspoon(s)'),
        ('Drop', 'Drop(s)'),
        ('Application', 'Application(s)'),
        ('Patch', 'Patch(es)'),
    ]

    # This links the medicine directly to the specific consultation
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    
    # The individual details from the UI design
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=50, help_text="e.g., 500mg")
    form = models.CharField(max_length=20, choices=FORM_CHOICES, default='Tablet')
    frequency = models.CharField(max_length=100, help_text="e.g., 3 times a day")

    def __str__(self):
        return f"{self.medicine_name} ({self.dosage}) - {self.appointment.patient.last_name}"