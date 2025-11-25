from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'complaints'

urlpatterns = [
    path('submit_complaint/', views.submit_complaint , name='submit_complaint'),
    path('my_complaints/', views.my_complaints, name='my_complaints'),
    path('submitted/', TemplateView.as_view(
        template_name='complaints/submitted.html'), name='submit_success'),
]
