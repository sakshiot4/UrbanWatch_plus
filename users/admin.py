from django.contrib import admin
from .models import Citizen

# Register your models here.

#admin.site.register(Citizen, CitizenAdmin)

@admin.register(Citizen)
class CitizenAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'address', 'region', 'is_registered']
    search_fields = ['name', 'user__username', 'user__email']
    list_filter = ['region', 'is_registered']
