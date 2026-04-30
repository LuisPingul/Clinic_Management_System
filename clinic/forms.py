from django import forms
from .models import Patient, Appointment

# --- 1. REGISTER PATIENT FORM ---
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'phone_number', 'date_of_birth',
                  'sex', 'height', 'weight', 'blood_type', 'comorbidities', 'allergies']
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['height'].required = False
            self.fields['weight'].required = False
            self.fields['blood_type'].required = False
            self.fields['comorbidities'].required = False
            self.fields['allergies'].required = False


        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0917-123-4567'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'type': 'date'}),

            'sex': forms.Select(attrs={'class': 'form-select'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 170cm'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 70kg'}),
            'blood_type': forms.Select(attrs={'class': 'form-select'}),

            'comorbidities': forms.HiddenInput(attrs={'id': 'id_comorbidites'}),
            'allergies': forms.HiddenInput(attrs={'id': 'id_allergies'}),
        }

# --- 2. BOOK APPOINTMENT FORM (NEW) ---
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        # Notice we don't include the "Symptoms" or "Diagnosis" here, because only the Doctor fills those out later!
        fields = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'is_walk_in', 'status']
        
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            # Here is the magic 'type': 'time' that creates the visual clock!
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}), 
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


# --- 3. DOCTOR'S CONSULTATION FORM (NEW) ---
class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Appointment
        # The doctor only interacts with the medical data and the final status
        fields = ['symptoms', 'doctor_diagnosis', 'doctor_recommendation', 'prescription_details', 'status']
        
        widgets = {
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'doctor_diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'doctor_recommendation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prescription_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }