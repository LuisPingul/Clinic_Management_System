from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_patient, name='register_patient'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('consultation/<int:pk>/', views.consultation, name='consultation'),
    path('prescription/<int:pk>/', views.print_prescription, name='print_prescription'),
    path('record/<int:pk>/', views.view_record, name='view_record'),
    path('patient/login/', views.patient_login, name='patient_login'),
    path('patient/portal/', views.patient_portal, name='patient_portal'),
    path('patient/logout/', views.patient_logout, name='patient_logout'),
    path('update_status/<int:pk>/', views.update_status, name='update_status'),
    path('switch-role/<str:role>/', views.switch_role, name='switch_role'),
    path('patient/update/<int:pk>/', views.update_patient, name='update_patient'),
    path('patient/profile/<int:pk>/', views.view_patient, name='view_patient'),
    path('patient/delete/<int:pk>/', views.delete_patient, name='delete_patient'),
]