from django.urls import path
from . import views

urlpatterns = [
    # This links the root of the theme app to your home view logic
    path('', views.home, name='home'),
]