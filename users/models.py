from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Create your models here.
class Citizen(models.Model):

    REGION_CHOICES = (
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('central', 'Central'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, 
                                related_name='citizen_profile')
    name = models.CharField(max_length=255, help_text="Full name (required)")
    phone = models.CharField(max_length=10, validators=[
        RegexValidator(regex=r'^[0-9]{10}$',
                       message="Phone number must be 10 digits",
                       code='invalid_phone',
        )], help_text="10-digit phone number (required)")
    
    address = models.CharField(max_length=255, help_text="Residential address (required)")
    region = models.CharField(max_length=100, choices=REGION_CHOICES, help_text="Region (required)")
    is_registered = models.BooleanField(default=True , help_text="Account registration status")
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.user.username})"