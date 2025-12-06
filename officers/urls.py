from django.urls import path
from . import views

app_name = 'officers'

urlpatterns = [
    # Define your complaint-related URL patterns here.
    path('dashboard/', views.officer_dashboard, name='dashboard'),
    path('assign/<int:complaint_id>/', views.assign_to_me, name='assign_to_me'),
    path('complaint/<int:complaint_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaint/<int:complaint_id>/update-status/', views.update_status, name='update_status'), 
    path('complaint/<int:complaint_id>/assign-contractor/', views.assign_contractor, name='assign_contractor'),
]
