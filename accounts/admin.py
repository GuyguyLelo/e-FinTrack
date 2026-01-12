"""
Admin pour les modèles accounts
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['nom_service', 'description', 'actif', 'date_creation']
    list_filter = ['actif']
    search_fields = ['nom_service', 'description']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'service', 'actif', 'date_creation']
    list_filter = ['role', 'service', 'actif', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations DGRAD', {
            'fields': ('role', 'service', 'telephone', 'actif')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations DGRAD', {
            'fields': ('role', 'service', 'telephone', 'actif')
        }),
    )

