from django.contrib import admin
from .models import Officer

@admin.register(Officer)
class OfficerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'region']
    search_fields = ['name', 'email', 'region']
    list_filter = ['region']
