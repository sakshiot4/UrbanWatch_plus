from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from users.models import Citizen
from officers.models import Officer
from contractors.models import Contractor

import uuid

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('water', 'Water Supply'),
        ('road', 'Road & Infrastructure'),
        ('electricity', 'Electricity'),
        ('sanitation', 'Sanitation'),
        ('other', 'Other'),
    ]

    REGION_CHOICE = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('central', 'Central'),
    ]
    
    # Foreign Keys matching your schema
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE, related_name='complaints')
    officer = models.ForeignKey(Officer, null=True, blank=True, 
                    on_delete=models.SET_NULL, related_name='officer_assigned_complaints')
    contractor = models.ForeignKey(Contractor, null=True, blank=True, 
                    on_delete=models.SET_NULL, related_name='contractor_assigned_complaints')
    
    # Core fields from your schema
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,
                               default='reported')
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    region = models.CharField(max_length=50, choices=REGION_CHOICE)
    # Additional fields (not in schema but useful)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    proof_image = models.ImageField(upload_to='complaint_proofs/', null=True, blank=True)
    tracking_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    completion_image = models.ImageField(upload_to='complaint_proofs/', null=True, blank=True)

    officer_feedback = models.TextField(null=True, blank=True, help_text="Officer feedback when work is rejected.")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    assigned_at = models.DateTimeField(null=True, blank=True)
    in_progress_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']

    # Define allowed status transitions. 
    # Meanss a complaint can only move to certain statuses from its current status.
    STATUS_TRANSITIONS = {
        'reported': ['assigned'],
        'assigned': ['in_progress'],
        'in_progress': ['completed', 'assigned'],
        'completed': ['closed', 'in_progress'],
        'closed': []
    }

    def can_transition_to(self, new_status):
        """Check if the complaint can transition to the new status."""
        return new_status in self.STATUS_TRANSITIONS.get(self.status, [])
    
    def clean(self):
        if self.status == 'completed' and not self.completion_image:
            raise ValidationError("Completion image is required to mark as completed.")

    
    def __str__(self):
        return f"{self.title} ({self.status})"
