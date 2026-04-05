"""
Configuration de l'application RBAC (Role-Based Access Control)
"""
from django.apps import AppConfig


class RbacConfig(AppConfig):
    name = 'rbac'
    verbose_name = 'Gestion des Permissions'
