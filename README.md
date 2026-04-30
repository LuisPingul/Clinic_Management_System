🏥 JMCFI Clinic Management System

A comprehensive, multi-role web application built with Django and Bootstrap 5 to streamline clinic operations. This system handles the entire patient lifecycle: from front-desk registration and queue management to doctor consultations and patient-accessible digital prescriptions.

📑 Table of Contents

- Features by Role
    - Front Desk / Admin Dashboard
    - Doctor Dashboard
    - Patient Portal
- Technology Stack
- Core System Mechanics
- Clinical Workflow Walkthrough
- Installation & Setup



🚀 Features by Role

1. Front Desk / Admin Dashboard

The command center for clinic receptionists and administrators.

- Patient Management: Register new patients, search the directory, update biographical data, and securely remove patients (with cascading record deletion).

- Appointment Booking: Schedule visits for patients with specific doctors.

- Smart Queue System: \* Divided into three sub-tabs: Previous (Historical), Today (Live Queue), and Future (Upcoming).

    - Live Status Tracking: Dropdown menus allow the admin to instantly update patient states (Scheduled, Waiting in Lobby, Late, In Consultation, Cleared, No-Show) using asynchronous Fetch API requests without reloading the page.

- Comprehensive Profiles: Access a patient's full visit history, vitals, comorbidities, and allergies from a single screen.


2. Doctor Dashboard

A personalized workspace for medical professionals.

- Role Switching: Doctors can view the system through their specific lens, filtering out irrelevant clinic noise.

- Schedule Management: View pending consultations for the day and upcoming appointments.

- Active Consultation Module: \* Update patient vitals (Height, Weight).

    - Record Symptoms, Doctor's Diagnosis, and Medical Recommendations.

    - Prescription Engine: Dynamically prescribe multiple medications (Medicine, Dosage, Form, Frequency) in a single consultation.

    - Automatically updates the patient's front-desk status to Cleared once the consultation is submitted.

- Historical Access: View past consultations and a dedicated list of "My Patients".


3. Patient Portal

A secure, self-service portal for patients to access their medical records.

    - 4-Point Security Login: Requires Exact First Name, Exact Last Name, Registered Phone Number, and Date of Birth to grant access.

    - Visit History: Patients can review past diagnoses and doctor recommendations.

    - Digital Prescriptions: \* Automatically generates an official, print-ready PDF prescription (complete with traditional Rx iconography).

        - Context-aware navigation ensures patients remain in their secure portal when viewing records.


🛠️ Technology Stack

- Backend: Python 3.11, Django 5.2.x

- Frontend: HTML5, CSS3, Vanilla JavaScript (Fetch API for AJAX)

- UI Framework: Bootstrap 5.3 (via CDN)

- Database: SQLite (Default Django DB)


⚙️ Core System Mechanics & Highlights

- Context-Aware Navigation ("Smart Buttons"): The system detects the user's current session (admin, doctor\_id, or patient\_id) and dynamically alters "Back" buttons to route the user to their appropriate dashboard, preventing unauthorized role-crossing.

- Print-Optimized Views: The Prescription Pad utilizes specific @media print CSS rules to hide UI buttons and render a clean, professional, US Letter/A4 formatted medical document.

- Security Measures: \* @require\_POST decorators and {% csrf\_token %} implementation on destructive actions (like patient deletion and status updates).

    - Strict session checks prevent patients from manipulating URLs to view other patients' prescriptions.


🏥 Clinical Workflow Walkthrough

1. Walk-in / Call: Front desk registers a Patient and books an Appointment.

2. Arrival: Admin updates status to Waiting in Lobby.

3. Consultation: Doctor clicks "Consult", reviews history, enters diagnosis, inputs prescriptions, and clicks Save.

4. Checkout: Patient is automatically marked as Cleared.

5. Post-Visit: Patient logs into the portal using their details to view their notes and print their Official Prescription.


💻 Installation & Setup

1. Clone the repository:

- git clone <your-repository-url>
- cd clinical\_system

2. Set up a Virtual Environment:

- python -m venv env
- source env/bin/activate # On Windows use: env\Scripts\activate

3. Install Dependencies:

- pip install django

4. Apply Migrations:

- python manage.py makemigrations clinic
- python manage.py migrate

5. Run the Development Server:

- python manage.py runserver

The system will be accessible at http://127.0.0.1:8000/
