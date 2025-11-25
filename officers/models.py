from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Officer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                                related_name='officer_profile')
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=100, blank=True)
    #department = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Officer: {self.name}"