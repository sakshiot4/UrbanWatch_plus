from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Define your complaint-related URL patterns here
    path('dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('complaint/<int:complaint_id>/status/', views.complaint_status_detail, name='complaint_status_detail'),
]