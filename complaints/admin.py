from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['title', 'citizen', 'status', 'category', 'region', 'created_at']
    list_filter = ['status', 'region', 'category', 'created_at']
    search_fields = ['title', 'description', 'citizen__name', 'region']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('title', 'description', 'category', 'location', 'proof_image', 'region')
        }),
        ('Assignment', {
            'fields': ('citizen', 'officer', 'contractor', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
