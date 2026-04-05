"""
URLs pour la gestion des permissions et rôles
"""
from django.urls import path, include
from . import views

app_name = 'rbac'

urlpatterns = [
    # Interface basée sur les modèles Django (NOUVEAU SYSTÈME)
    path('modeles/', include('rbac.urls_modeles')),
    
    # Ancien système (conservé pour compatibilité)
    path('roles/', views.RoleListView.as_view(), name='role_liste'),
    path('roles/creer/', views.RoleCreateView.as_view(), name='role_creer'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role_detail'),
    path('roles/<int:pk>/modifier/', views.RoleUpdateView.as_view(), name='role_modifier'),
    path('roles/<int:pk>/supprimer/', views.RoleDeleteView.as_view(), name='role_supprimer'),
    
    # Gestion des permissions
    path('permissions/', views.PermissionListView.as_view(), name='permission_liste'),
    path('permissions/creer/', views.PermissionCreateView.as_view(), name='permission_creer'),
    path('permissions/<int:pk>/', views.PermissionDetailView.as_view(), name='permission_detail'),
    path('permissions/<int:pk>/modifier/', views.PermissionUpdateView.as_view(), name='permission_modifier'),
    path('permissions/<int:pk>/supprimer/', views.PermissionDeleteView.as_view(), name='permission_supprimer'),
    
    # Gestion des permissions de rôle
    path('roles/<int:role_id>/permissions/', views.RolePermissionView.as_view(), name='role_permissions'),
    path('roles/<int:role_id>/permissions/ajouter/', views.AddRolePermissionView.as_view(), name='role_permission_ajouter'),
    path('roles/<int:role_id>/permissions/<int:permission_id>/retirer/', views.RemoveRolePermissionView.as_view(), name='role_permission_retirer'),
    
    # API pour vérifier les permissions
    path('api/check/', views.CheckPermissionView.as_view(), name='api_check_permission'),
]
