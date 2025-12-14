from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/contractor/', views.contractor_signup,
         name='contractor_signup'),
    
]
