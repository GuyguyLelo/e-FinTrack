"""
URLs pour l'interface RBAC basée sur les modèles Django
"""
from django.urls import path
from . import views_modeles

app_name = 'rbac_modeles'

urlpatterns = [
    # Permissions basées sur les modèles
    path('permissions/', views_modeles.PermissionModeleListView.as_view(), name='permission_modele_list'),
    path('permissions/creer/', views_modeles.PermissionModeleCreateView.as_view(), name='permission_modele_create'),
    path('permissions/<int:pk>/modifier/', views_modeles.PermissionModeleUpdateView.as_view(), name='permission_modele_update'),
    
    # Rôles basés sur les modèles
    path('roles/', views_modeles.RoleModeleListView.as_view(), name='role_modele_list'),
    path('roles/creer/', views_modeles.RoleModeleCreateView.as_view(), name='role_modele_create'),
    path('roles/<int:pk>/', views_modeles.RoleModeleDetailView.as_view(), name='role_modele_detail'),
    path('roles/<int:pk>/modifier/', views_modeles.RoleModeleUpdateView.as_view(), name='role_modele_update'),
    path('roles/<int:pk>/permissions/', views_modeles.RoleModelePermissionsView.as_view(), name='role_modele_permissions'),
    
    # Tableau de bord
    path('dashboard/', views_modeles.dashboard_rbac_modeles, name='dashboard_rbac_modeles'),
]
