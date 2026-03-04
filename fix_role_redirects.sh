#!/bin/bash
# fix_role_redirects.sh - Correction des redirections par rôle

set -e

echo "🎯 Correction des Redirections par Rôle"
echo "===================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Analyse de l'état actuel..."

python manage.py shell << 'EOF'
from accounts.models import User

print("📊 État actuel des utilisateurs:")
print("=" * 50)

users = User.objects.all().order_by('username')
for user in users:
    crown = "👑" if user.is_superuser else "👤"
    print(f"{crown} {user.username}")
    print(f"   Role: {user.role}")
    print(f"   Superuser: {user.is_superuser}")
    print(f"   Staff: {user.is_staff}")
    print(f"   Actif: {user.is_active}")
    print("")

EOF

echo "🔧 2. Configuration des rôles et redirections..."

python manage.py shell << 'EOF'
from accounts.models import User

# Configuration des rôles et permissions
print("🔧 Configuration des rôles:")

# 1. AdminDaf - Uniquement les natures
try:
    admin_daf = User.objects.get(username='AdminDaf')
    admin_daf.role = 'CD_FINANCE'      # Rôle finance
    admin_daf.is_superuser = False        # Pas d'accès admin Django
    admin_daf.is_staff = False            # Pas d'accès admin Django
    admin_daf.is_active = True
    admin_daf.save()
    print("✅ AdminDaf configuré:")
    print(f"   Role: {admin_daf.role}")
    print(f"   Accès: Natures économiques UNIQUEMENT")
    print(f"   Redirection: /demandes/natures/")
except User.DoesNotExist:
    print("❌ AdminDaf non trouvé")

# 2. DirDaf - Tableau de bord et clotures
try:
    dirdaf = User.objects.get(username='DirDaf')
    dirdaf.role = 'DG'                   # Rôle direction
    dirdaf.is_superuser = False            # Pas d'accès admin Django
    dirdaf.is_staff = False                # Pas d'accès admin Django
    dirdaf.is_active = True
    dirdaf.save()
    print("✅ DirDaf configuré:")
    print(f"   Role: {dirdaf.role}")
    print(f"   Accès: Tableau de bord + Clotures")
    print(f"   Redirection: /dashboard/")
except User.DoesNotExist:
    print("❌ DirDaf non trouvé")

# 3. DivDaf - Tableau de bord et clotures
try:
    divdaf = User.objects.get(username='DivDaf')
    divdaf.role = 'CD_FINANCE'           # Rôle chef finance
    divdaf.is_superuser = False            # Pas d'accès admin Django
    divdaf.is_staff = False                # Pas d'accès admin Django
    divdaf.is_active = True
    divdaf.save()
    print("✅ DivDaf configuré:")
    print(f"   Role: {divdaf.role}")
    print(f"   Accès: Tableau de bord + Clotures")
    print(f"   Redirection: /dashboard/")
except User.DoesNotExist:
    print("❌ DivDaf non trouvé")

# 4. SuperAdmin - Accès complet SAUF natures
try:
    superadmin = User.objects.get(username='SuperAdmin')
    superadmin.role = 'ADMIN'               # Rôle admin
    superadmin.is_superuser = True            # Accès admin Django
    superadmin.is_staff = True                # Accès interface admin
    superadmin.is_active = True
    superadmin.save()
    print("✅ SuperAdmin configuré:")
    print(f"   Role: {superadmin.role}")
    print(f"   Accès: Tableau de bord + Recettes + Dépenses + Admin Django")
    print(f"   Redirection: /dashboard/ (pas les natures)")
except User.DoesNotExist:
    print("❌ SuperAdmin non trouvé")

# 5. OpsDaf - Saisie recettes et dépenses
try:
    opsdaf = User.objects.get(username='OpsDaf')
    opsdaf.role = 'OPERATEUR_SAISIE'     # Rôle saisie
    opsdaf.is_superuser = False            # Pas d'accès admin Django
    opsdaf.is_staff = False                # Pas d'accès admin Django
    opsdaf.is_active = True
    opsdaf.save()
    print("✅ OpsDaf configuré:")
    print(f"   Role: {opsdaf.role}")
    print(f"   Accès: Saisie recettes + dépenses")
    print(f"   Redirection: /recettes/feuille/")
except User.DoesNotExist:
    print("❌ OpsDaf non trouvé")

EOF

echo ""
echo "🌐 3. Création de la vue de login avec redirections par rôle..."

cat > accounts/views_login_fixed.py << 'LOGIN_VIEW'
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings

def login_view_fixed(request):
    """Vue de login avec redirections par rôle"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirection selon le rôle
            if user.role == 'ADMIN':
                # SuperAdmin: Tableau de bord complet (pas les natures)
                return redirect('/dashboard/')
            elif user.role == 'CD_FINANCE':
                if user.username == 'AdminDaf':
                    # AdminDaf: Uniquement les natures
                    return redirect('/demandes/natures/')
                else:
                    # DivDaf: Tableau de bord et clotures
                    return redirect('/dashboard/')
            elif user.role == 'DG':
                # DirDaf: Tableau de bord et clotures
                return redirect('/dashboard/')
            elif user.role == 'OPERATEUR_SAISIE':
                # OpsDaf: Saisie recettes et dépenses
                return redirect('/recettes/feuille/')
            else:
                # Défaut
                return redirect(getattr(settings, 'LOGIN_REDIRECT_URL', '/'))
        else:
            messages.error(request, 'Identifiants invalides')
    
    return render(request, 'accounts/login.html')

print("✅ Vue de login avec redirections par rôle créée")
print("   Fichier: accounts/views_login_fixed.py")
LOGIN_VIEW

echo ""
echo "🔧 4. Création des décorateurs de permission..."

cat > accounts/role_permissions.py << 'ROLE_DECORATORS'
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def role_required(allowed_roles):
    """Décorateur pour vérifier les rôles"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'role'):
                messages.error(request, "Rôle non défini")
                return redirect('accounts:login')
                
            if request.user.role not in allowed_roles:
                messages.error(request, "Accès non autorisé pour votre rôle")
                return redirect('accounts:login')
                
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Décorateurs spécifiques par rôle
def admin_only(view_func):
    """Uniquement SuperAdmin"""
    return role_required(['ADMIN'])(view_func)

def finance_manager_only(view_func):
    """AdminDaf, DivDaf, DirDaf, SuperAdmin"""
    return role_required(['ADMIN', 'CD_FINANCE', 'DG'])(view_func)

def management_only(view_func):
    """DirDaf, DivDaf, SuperAdmin"""
    return role_required(['ADMIN', 'CD_FINANCE', 'DG'])(view_func)

def operator_only(view_func):
    """OpsDaf et SuperAdmin"""
    return role_required(['ADMIN', 'OPERATEUR_SAISIE'])(view_func)

def natures_only(view_func):
    """AdminDaf uniquement pour les natures"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.username != 'AdminDaf' or request.user.role != 'CD_FINANCE':
                messages.error(request, "Accès aux natures réservé à AdminDaf")
                return redirect('accounts:login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

print("✅ Décorateurs de rôle créés")
print("   Fichier: accounts/role_permissions.py")
ROLE_DECORATORS

echo ""
echo "📝 5. Exemple d'utilisation dans les vues..."

cat > accounts/views_example_usage.py << 'EXAMPLE_USAGE'
from django.shortcuts import render
from .role_permissions import (
    admin_only, finance_manager_only, management_only, 
    operator_only, natures_only
)

# Vue accessible uniquement par SuperAdmin
@admin_only
def dashboard_admin(request):
    """Tableau de bord pour SuperAdmin"""
    return render(request, 'dashboard_admin.html')

# Vue accessible par AdminDaf uniquement
@natures_only
def nature_liste(request):
    """Liste des natures - AdminDaf uniquement"""
    return render(request, 'demandes/nature_liste.html')

# Vue accessible par DirDaf, DivDaf, SuperAdmin
@management_only
def cloture_liste(request):
    """Gestion des clotures - Direction uniquement"""
    return render(request, 'clotures/cloture_liste.html')

# Vue accessible par OpsDaf et SuperAdmin
@operator_only
def recette_feuille(request):
    """Saisie des recettes - Opérateurs"""
    return render(request, 'recettes/recette_feuille.html')

print("✅ Exemples d'utilisation créés")
print("   Fichier: accounts/views_example_usage.py")
EXAMPLE_USAGE

echo ""
echo "🎯 6. Résumé des permissions configurées..."

python manage.py shell << 'EOF'
from accounts.models import User

print("📊 Résumé final des permissions:")
print("=" * 60)

users = User.objects.all().order_by('username')
for user in users:
    crown = "👑" if user.is_superuser else "👤"
    
    # Déterminer l'accès selon le rôle
    if user.username == 'AdminDaf':
        access = "Natures économiques UNIQUEMENT"
        redirect = "/demandes/natures/"
    elif user.username == 'SuperAdmin':
        access = "Tableau de bord + Recettes + Dépenses + Admin Django"
        redirect = "/dashboard/"
    elif user.role in ['DG', 'CD_FINANCE'] and user.username != 'AdminDaf':
        access = "Tableau de bord + Clotures"
        redirect = "/dashboard/"
    elif user.role == 'OPERATEUR_SAISIE':
        access = "Saisie recettes + dépenses"
        redirect = "/recettes/feuille/"
    else:
        access = "Non défini"
        redirect = "/"
    
    print(f"{crown} {user.username} ({user.role})")
    print(f"   🌐 Accès: {access}")
    print(f"   🔄 Redirection: {redirect}")
    print("")

EOF

echo ""
echo "🔧 7. Instructions pour appliquer les changements..."
echo "================================================"

echo "📝 Étape 1: Remplacer la vue de login"
echo "1. Copiez la nouvelle vue de login:"
echo "   cp accounts/views_login_fixed.py accounts/views_login_new.py"
echo ""
echo "2. Modifiez vos URLs pour utiliser la nouvelle vue:"
echo "   Dans accounts/urls.py, remplacez:"
echo "   path('login/', views.LoginView.as_view(), name='login')"
echo "   Par:"
echo "   path('login/', views.login_view_fixed, name='login')"

echo ""
echo "📝 Étape 2: Appliquer les décorateurs aux vues"
echo "1. Importez les décorateurs:"
echo "   from accounts.role_permissions import natures_only, admin_only"
echo ""
echo "2. Appliquez aux vues existantes:"
echo "   @natures_only")
echo "   def nature_liste(request):")
echo "       # AdminDaf uniquement")
echo ""
echo "   @admin_only")
echo "   def dashboard_admin(request):")
echo "       # SuperAdmin uniquement")

echo ""
echo "🔄 Étape 3: Redémarrer les services"
echo "sudo systemctl restart gunicorn"
echo "sudo systemctl restart nginx"

echo ""
echo "🌐 Étape 4: Tester les connexions"
echo "=================================="
echo "👤 AdminDaf:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: AdminDaf / AdminDaf123!"
echo "   Résultat: /demandes/natures/ ✅"
echo ""
echo "👑 SuperAdmin:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: SuperAdmin / SuperAdmin123!"
echo "   Résultat: /dashboard/ ✅"
echo ""
echo "👤 DirDaf:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: DirDaf / DirDaf123!"
echo "   Résultat: /dashboard/ ✅"
echo ""
echo "👤 DivDaf:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: DivDaf / DivDaf123!"
echo "   Résultat: /dashboard/ ✅"

echo ""
echo "✅ Configuration des redirections par rôle terminée !"
echo "🎊 Appliquez les changements pour finaliser"
