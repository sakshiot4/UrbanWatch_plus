from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Citizen(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                                related_name='citizen_profile')
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=255, blank=True)
    region = models.CharField(max_length=100, blank=True)
    is_registered = models.BooleanField(default=True)

    def __str__(self):
        return f"Citizen: {self.name}"