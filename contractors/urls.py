from django.urls import path
from . import views

app_name = 'contractors'

urlpatterns = [
    # Define your complaint-related URL patterns here
    path('dashboard/', views.contractor_dashboard, name = 'contractor_dashboard'),
    path('complaint/<int:complaint_id>/', views.contractor_complaint_detail, name='contractor_complaint_detail'),
    path('complaint/<int:complaint_id>/update-status/', views.contractor_update_status, name='contractor_update_status'),
    path('for-complaint/<int:complaint_id>/', 
         views.contractor_list_for_complaint, name = 'list_for_complaint'),
]
