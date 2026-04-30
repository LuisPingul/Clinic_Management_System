import json
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Appointment, Patient, Doctor, PrescriptionItem
from .forms import PatientForm, AppointmentForm, ConsultationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def home(request):
    # 1. SESSION INITIALIZATION
    # If the user visits the dashboard, we assume they are Staff (Admin/Doctor).
    # We set 'active_role' if it doesn't exist to prevent the navigation bug.
    if 'active_role' not in request.session:
        request.session['active_role'] = 'admin'
    
    active_role = request.session.get('active_role')
    
    # 2. DATA INITIALIZATION
    selected_doctor = None
    my_schedule_today, future_appointments, past_consultations, my_patients = [], [], [], []
    today = timezone.localtime(timezone.now()).date()
    doctors = Doctor.objects.all()

    # 3. ADMIN QUEUE CATEGORIES
    past_admin = Appointment.objects.filter(appointment_date__lt=today).order_by('-appointment_date', '-appointment_time')
    today_admin = Appointment.objects.filter(appointment_date=today).order_by('appointment_time')
    future_admin = Appointment.objects.filter(appointment_date__gt=today).order_by('appointment_time')

    # Debugging Console Output
    print(f"DEBUG: Today is {today}. Past: {past_admin.count()}, Today: {today_admin.count()}, Future: {future_admin.count()}")

    # 4. PATIENT SEARCH LOGIC
    patients = Patient.objects.all()
    search_query = request.GET.get('search')
    if search_query:
        patients = patients.filter(Q(last_name__icontains=search_query) | Q(first_name__icontains=search_query))

    # 5. DOCTOR SPECIFIC DATA
    # Only run this if the active_role is a specific Doctor's ID
    if active_role != 'admin':
        try:
            selected_doctor = Doctor.objects.get(id=int(active_role))
            my_schedule_today = Appointment.objects.filter(doctor=selected_doctor, appointment_date__lte=today).exclude(status='CLEARED').order_by('appointment_date', 'appointment_time')
            future_appointments = Appointment.objects.filter(doctor=selected_doctor, appointment_date__gt=today).order_by('appointment_date', 'appointment_time')
            past_consultations = Appointment.objects.filter(doctor=selected_doctor, status='CLEARED').order_by('-appointment_date', '-appointment_time')
            my_patients = Patient.objects.filter(appointments__doctor=selected_doctor).distinct()
        except (ValueError, Doctor.DoesNotExist):
            request.session['active_role'] = 'admin'
            active_role = 'admin'

    context = {
        'active_role': active_role,
        'doctors': doctors,            
        'selected_doctor': selected_doctor,
        'today': today,
        'past_admin': past_admin,
        'today_admin': today_admin,
        'future_admin': future_admin,
        'patients': patients,
        'search_query': search_query, 
        'my_schedule_today': my_schedule_today,
        'future_appointments': future_appointments,
        'past_consultations': past_consultations,
        'my_patients': my_patients,
    } 
    return render(request, 'clinic/home.html', context)


def register_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PatientForm()
    
    return render(request, 'clinic/register_patient.html', {'form': form})

def view_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    # Fetch all past visits for this specific patient
    history = patient.appointments.all().order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'clinic/view_patient.html', {
        'patient': patient,
        'history': history
    })


def update_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    
    if request.method == 'POST':
        # instance=patient tells Django to update the existing record instead of creating a new one
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        # Pre-fill the form with the patient's current data
        form = PatientForm(instance=patient)
    
    return render(request, 'clinic/update_patient.html', {'form': form, 'patient': patient})


def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = AppointmentForm()
    
    return render(request, 'clinic/book_appointment.html', {'form': form})



def consultation(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    patient = appointment.patient

    if request.method == 'GET':
        if appointment.status in ['SCHEDULED', 'WAITING']:
            appointment.status = 'IN_CONSULTATION'
            appointment.save()

    if request.method == 'POST':
        # 1. Update medical details
        patient.height = request.POST.get('height') or patient.height
        patient.weight = request.POST.get('weight') or patient.weight
        patient.blood_type = request.POST.get('blood_type') or patient.blood_type
        patient.comorbidities = request.POST.get('comorbidities') or patient.comorbidities
        patient.allergies = request.POST.get('allergies') or patient.allergies
        patient.save()
        appointment.symptoms = request.POST.get('symptoms')
        appointment.doctor_diagnosis = request.POST.get('diagnosis')
        appointment.doctor_recommendation = request.POST.get('recommendation')
        
        # 2. FORCE STATUS UPDATE TO CLEARED
        # This ensures the Front Desk sees the patient as finished
        appointment.status = 'CLEARED'
        
        appointment.save()

        # 3. Handle Prescription Items
        medicines_json = request.POST.get('medicines_data')
        if medicines_json:
            try:
                medicines_list = json.loads(medicines_json)
                appointment.prescriptions.all().delete()

                for med in medicines_list:
                    PrescriptionItem.objects.create(
                        appointment=appointment,
                        medicine_name=med['name'],
                        dosage=med['dosage'],
                        form=med['form'],
                        frequency=med['frequency']
                    )
            except json.JSONDecodeError:
                pass # Handle potential JSON errors silently or add logging

        return redirect('home')
        
    return render(request, 'clinic/consultation.html', {'appointment': appointment})


def print_prescription(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    patient_id = request.session.get('patient_id')
    if patient_id and appointment.patient.id != patient_id:
        return redirect('patient-portal')

    return render(request, 'clinic/prescription_pad.html', {'appointment': appointment})

# --- PATIENT PORTAL VIEWS ---
def patient_login(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone_number')
        dob = request.POST.get('date_of_birth')

        try:
            # Try to find the patient that matches all 4 fields (for better security than just phone or DOB alone)
            patient = Patient.objects.get(
                first_name__iexact=first_name, # Case-insensitive match
                last_name__iexact=last_name, 
                phone_number=phone, 
                date_of_birth=dob
            )
            # Log them in by securely saving their ID in the browser's session
            request.session['patient_id'] = patient.id
            return redirect('patient_portal')
        except Patient.DoesNotExist:
            # If they type it wrong , show an error message
            return render(request, 'clinic/patient_login.html', {
                'error': 'Patient details not found. Please ensure your name and details match your registration.'
            })
        
    return render(request, 'clinic/patient_login.html')
    
def patient_portal(request):
    # Security check: Make sure they are actually logged in
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    
    patient = get_object_or_404(Patient, id=patient_id)

    # split their appointments into "Upcoming" and "Past/Cleared"
    upcoming_appointments = patient.appointments.exclude(status='CLEARED').order_by('appointment_date', 'appointment_time')
    past_appointments = patient.appointments.filter(status='CLEARED').order_by('-appointment_date', '-appointment_time')

    context = {
        'patient': patient,
        'upcoming': upcoming_appointments,
        'past': past_appointments,
    }
    return render(request, 'clinic/patient_portal.html', context)


def patient_logout(request):
    # Clear the patient's session to log them out
    if 'patient_id' in request.session:
        del request.session['patient_id']
    return redirect('patient_login')


def switch_role(request, role):
    request.session['active_role'] = role
    return redirect('home')

def view_record(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    # 1. PRIORITY: Check if the user is acting as Staff (Admin or Doctor)
    if request.session.get('active_role'):
        back_url = 'home'
        back_label = 'Back to Dashboard'
        
    # 2. SECONDARY: Check if they are just a Patient
    elif request.session.get('patient_id'):
        back_url = 'patient_portal'
        back_label = 'Back to Portal'
        
    # 3. FALLBACK
    else:
        back_url = 'home'
        back_label = 'Back to Dashboard'

    return render(request, 'clinic/view_record.html', {
        'appointment': appointment,
        'back_url': back_url,
        'back_label': back_label
    })


@require_POST
def update_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status')

    if new_status:
        appointment.status = new_status
        appointment.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@require_POST
def delete_patient(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    patient.delete()
    return redirect('home')