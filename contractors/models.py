from django.db import models
from django.contrib.auth.models import User

class Contractor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='contractor_profile')
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Contractor: {self.name}"
