#!/bin/bash
# setup_role_permissions.sh - Configuration des permissions par rôle

set -e

echo "🎯 Configuration des Permissions par Rôle"
echo "====================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "👥 1. Configuration des rôles et permissions..."

python manage.py shell << 'EOF'
from accounts.models import User

# Mettre à jour les rôles et permissions
print("🔧 Configuration des utilisateurs...")

# 1. AdminDaf - Accès limité aux natures uniquement
try:
    admin_daf = User.objects.get(username='AdminDaf')
    admin_daf.role = 'CD_FINANCE'  # Rôle limité
    admin_daf.is_superuser = False    # Pas d'accès admin Django
    admin_daf.is_staff = False        # Pas d'accès admin Django
    admin_daf.is_active = True
    admin_daf.save()
    print("✅ AdminDaf configuré:")
    print(f"   Role: {admin_daf.role}")
    print(f"   Superuser: {admin_daf.is_superuser}")
    print(f"   Staff: {admin_daf.is_staff}")
    print(f"   Accès: Natures uniquement")
except User.DoesNotExist:
    print("❌ AdminDaf non trouvé")

# 2. SuperAdmin - Accès complet
try:
    superadmin = User.objects.get(username='SuperAdmin')
    superadmin.role = 'ADMIN'         # Rôle complet
    superadmin.is_superuser = True     # Accès admin Django complet
    superadmin.is_staff = True         # Accès interface admin
    superadmin.is_active = True
    superadmin.save()
    print("✅ SuperAdmin configuré:")
    print(f"   Role: {superadmin.role}")
    print(f"   Superuser: {superadmin.is_superuser}")
    print(f"   Staff: {superadmin.is_staff}")
    print(f"   Accès: Complet (dashboard, recettes, dépenses, admin)")
except User.DoesNotExist:
    print("❌ SuperAdmin non trouvé")

# 3. DirDaf - Accès direction
try:
    dirdaf = User.objects.get(username='DirDaf')
    dirdaf.role = 'DG'              # Rôle direction
    dirdaf.is_superuser = False       # Pas d'accès admin Django
    dirdaf.is_staff = False           # Pas d'accès admin Django
    dirdaf.is_active = True
    dirdaf.save()
    print("✅ DirDaf configuré:")
    print(f"   Role: {dirdaf.role}")
    print(f"   Superuser: {dirdaf.is_superuser}")
    print(f"   Staff: {dirdaf.is_staff}")
    print(f"   Accès: Direction limité")
except User.DoesNotExist:
    print("❌ DirDaf non trouvé")

# 4. OpsDaf - Accès saisie uniquement
try:
    opsdaf = User.objects.get(username='OpsDaf')
    opsdaf.role = 'OPERATEUR_SAISIE'  # Rôle saisie
    opsdaf.is_superuser = False         # Pas d'accès admin Django
    opsdaf.is_staff = False             # Pas d'accès admin Django
    opsdaf.is_active = True
    opsdaf.save()
    print("✅ OpsDaf configuré:")
    print(f"   Role: {opsdaf.role}")
    print(f"   Superuser: {opsdaf.is_superuser}")
    print(f"   Staff: {opsdaf.is_staff}")
    print(f"   Accès: Saisie uniquement")
except User.DoesNotExist:
    print("❌ OpsDaf non trouvé")

print("\n📊 Résumé des permissions:")
print("=" * 40)

users = User.objects.all().order_by('username')
for user in users:
    crown = "👑" if user.is_superuser else "👤"
    access = "Complet" if user.is_superuser else "Limité"
    print(f"{crown} {user.username} ({user.role}) - Accès: {access}")

EOF

echo ""
echo "🌐 2. Test des accès par rôle..."

python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User
from django.urls import reverse

# Test des accès pour chaque rôle
roles_test = [
    ('AdminDaf', 'CD_FINANCE', '/demandes/natures/'),
    ('SuperAdmin', 'ADMIN', '/dashboard/'),
    ('DirDaf', 'DG', '/dashboard/'),
    ('OpsDaf', 'OPERATEUR_SAISIE', '/recettes/feuille/'),
]

print("🧪 Test des accès par rôle:")
print("=" * 50)

for username, expected_role, test_url in roles_test:
    try:
        user = User.objects.get(username=username)
        client = Client()
        client.force_login(user)
        
        # Tester l'accès à l'URL
        response = client.get(test_url, follow=True)
        
        # Déterminer si l'accès devrait être autorisé
        should_have_access = False
        
        if username == 'SuperAdmin':
            should_have_access = True  # Accès à tout
        elif username == 'AdminDaf' and 'natures' in test_url:
            should_have_access = True  # Accès aux natures uniquement
        elif username == 'DirDaf' and 'dashboard' in test_url:
            should_have_access = True  # Accès au dashboard
        elif username == 'OpsDaf' and 'recettes' in test_url:
            should_have_access = True  # Accès aux recettes
            
        status = "✅" if response.status_code == 200 else "❌"
        expected = "✅" if should_have_access else "❌"
        result = "🎯" if (response.status_code == 200) == should_have_access else "⚠️"
        
        print(f"{result} {username} ({expected_role})")
        print(f"   URL: {test_url}")
        print(f"   Status: {response.status_code} {status}")
        print(f"   Attendu: {expected}")
        print(f"   Résultat: {result}")
        print("")
        
    except User.DoesNotExist:
        print(f"❌ {username} non trouvé")
    except Exception as e:
        print(f"❌ Erreur test {username}: {e}")

EOF

echo ""
echo "🔧 3. Configuration des redirections par rôle..."

python manage.py shell << 'EOF'
from django.urls import reverse
from django.conf import settings

print("📍 Configuration des redirections:")
print("=" * 40)

# Afficher la configuration actuelle
print(f"LOGIN_URL: {getattr(settings, 'LOGIN_URL', 'Non défini')}")
print(f"LOGIN_REDIRECT_URL: {getattr(settings, 'LOGIN_REDIRECT_URL', 'Non défini')}")

# Recommandations par rôle
print("\n🎯 Redirections recommandées par rôle:")
print("👑 SuperAdmin (ADMIN): /dashboard/ (accès complet)")
print("👤 AdminDaf (CD_FINANCE): /demandes/natures/ (limité)")
print("👤 DirDaf (DG): /dashboard/ (direction)")
print("👤 OpsDaf (OPERATEUR_SAISIE): /recettes/feuille/ (saisie)")

EOF

echo ""
echo "📝 4. Instructions pour implémenter les permissions..."
echo "================================================="

echo "🔧 Étape 1: Modifier les vues avec des décorateurs de rôle"
cat > role_decorators.py << 'DECORATOR'
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from accounts.models import User

def role_required(allowed_roles):
    """Décorateur pour vérifier les rôles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if not hasattr(request.user, 'role'):
                return redirect('accounts:login')
                
            if request.user.role not in allowed_roles:
                messages.error(request, "Accès non autorisé pour votre rôle")
                return redirect('accounts:login')
                
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_required(view_func):
    """Décorateur pour les admins uniquement"""
    return role_required(['ADMIN'])(view_func)

def finance_required(view_func):
    """Décorateur pour les finances uniquement"""
    return role_required(['ADMIN', 'CD_FINANCE', 'DG'])(view_func)

def saisie_required(view_func):
    """Décorateur pour les opérateurs de saisie"""
    return role_required(['ADMIN', 'CD_FINANCE', 'DG', 'OPERATEUR_SAISIE'])(view_func)
DECORATOR

echo "✅ Fichier de décorateurs créé: role_decorators.py"

echo ""
echo "🔧 Étape 2: Exemple d'utilisation dans les vues"
cat > view_example.py << 'EXAMPLE'
from role_decorators import admin_required, finance_required, saisie_required

# Vue accessible uniquement par SuperAdmin
@admin_required
def dashboard_admin(request):
    # Seul SuperAdmin (ADMIN) peut accéder
    return render(request, 'dashboard_admin.html')

# Vue accessible par AdminDaf (CD_FINANCE)
@finance_required
def natures_list(request):
    # AdminDaf peut voir les natures
    return render(request, 'demandes/nature_liste.html')

# Vue accessible par tous les utilisateurs authentifiés
@saisie_required
def recettes_list(request):
    # Tous peuvent voir les recettes
    return render(request, 'recettes/recette_feuille_liste.html')
EXAMPLE

echo "✅ Exemple d'utilisation créé: view_example.py"

echo ""
echo "🎯 5. Résumé des permissions configurées"
echo "========================================"
echo "👑 SuperAdmin (ADMIN):"
echo "   ✅ Accès dashboard complet"
echo "   ✅ Accès recettes"
echo "   ✅ Accès dépenses"
echo "   ✅ Accès admin Django"
echo "   ✅ Toutes les permissions"
echo ""
echo "👤 AdminDaf (CD_FINANCE):"
echo "   ✅ Accès /demandes/natures/ uniquement"
echo "   ❌ Pas d'accès admin Django"
echo "   ❌ Pas d'accès dashboard"
echo "   ❌ Accès limité aux natures"
echo ""
echo "👤 DirDaf (DG):"
echo "   ✅ Accès dashboard direction"
echo "   ✅ Accès rapports"
echo "   ❌ Pas d'accès admin Django"
echo ""
echo "👤 OpsDaf (OPERATEUR_SAISIE):"
echo "   ✅ Accès saisie recettes/dépenses"
echo "   ❌ Pas d'accès admin Django"
echo "   ❌ Accès limité"

echo ""
echo "🌐 6. Test de connexion par rôle"
echo "================================"
echo "Testez maintenant les connexions:"
echo ""
echo "👑 SuperAdmin:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: SuperAdmin / SuperAdmin123!"
echo "   Devrait voir: Dashboard complet"
echo ""
echo "👤 AdminDaf:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: AdminDaf / AdminDaf123!"
echo "   Devrait voir: /demandes/natures/ uniquement"
echo ""
echo "👤 DirDaf:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: DirDaf / DirDaf123!"
echo "   Devrait voir: Dashboard direction"
echo ""
echo "👤 OpsDaf:"
echo "   URL: http://187.77.171.80:8000/accounts/login/"
echo "   Login: OpsDaf / OpsDaf123!"
echo "   Devrait voir: Interface de saisie"

echo ""
echo "✅ Configuration des permissions terminée !"
echo "🎊 Implémentez les décorateurs dans vos vues pour finaliser"
