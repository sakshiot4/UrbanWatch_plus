from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['title', 'citizen', 'status', 'category', 'region', 'created_at', 'tracking_token']
    list_filter = ['status', 'region', 'category', 'created_at']
    search_fields = ['title', 'description', 'citizen__name', 'region']
    readonly_fields = ['created_at', 'updated_at', 'tracking_token']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'description', 'category', 'location', 'proof_image', 'region', 'tracking_token')
        }),
        ('Assignment', {
            'fields': ('citizen', 'officer', 'contractor', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
