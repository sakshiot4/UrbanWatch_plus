from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator  
from django.core.exceptions import ValidationError

class Contractor(models.Model):

    REGION_CHOICES = (
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('central', 'Central'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    CATEGORY_CHOICES = [
        ('water', 'Water Supply'),
        ('road', 'Road & Infrastructure'),
        ('electricity', 'Electricity'),
        ('sanitation', 'Sanitation'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                 related_name='contractor_profile')
    
    name = models.CharField(max_length=255, help_text="Full name (required)")
    email = models.EmailField(max_length=255, 
                    validators=[EmailValidator()], help_text="Valid email address (required)")
    
    phone = models.CharField(max_length=20,
                validators=[RegexValidator(regex = r'^[0-9]{10}$',
                message="Phone number must be 10 digits",code='invalid_phone',)]
                , help_text="10-digit phone number (required)")
    
    company_name = models.CharField(
        max_length=255,
        help_text="Company name (required)"
    )

    specialization = models.CharField(max_length=255, 
                        help_text="Area of expertise (required)")
    
    region = models.CharField(
        max_length=50,
        choices=REGION_CHOICES,
        help_text="Service region (required)"
    )
    
    
    license_number = models.CharField(
        max_length=100,
        #unique=True,
        help_text="License number (required, must be unique)"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Approval status by officer"
    )
    
    approved_by = models.ForeignKey(
        'officers.Officer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_contractors',
        help_text="Officer who approved this contractor"
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when approved"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if rejected)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.company_name}) - {self.get_status_display()}"
