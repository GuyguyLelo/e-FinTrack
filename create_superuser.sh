#!/bin/bash
# create_superuser.sh - Script pour créer un superuser Django complet

set -e

echo "👑 Création d'un Superuser Django Complet"
echo "========================================"

cd /var/www/e-fintrack

# Activer l'environnement virtuel
source venv/bin/activate

echo "🗑️  Vérification des superusers existants..."
python manage.py shell << EOF
from django.contrib.auth.models import User
from accounts.models import User as CustomUser

print("📊 Utilisateurs Django standards:")
for user in User.objects.all():
    print(f"   👤 {user.username} | Superuser: {user.is_superuser} | Staff: {user.is_staff}")

print("\n📊 Utilisateurs personnalisés:")
for user in CustomUser.objects.all():
    print(f"   👤 {user.username} | Role: {user.role} | Superuser: {user.is_superuser} | Staff: {user.is_staff}")

# Supprimer les anciens superusers si nécessaire
superusers = CustomUser.objects.filter(is_superuser=True)
if superusers.exists():
    print(f"\n🗑️  Suppression de {superusers.count()} ancien(s) superuser(s)...")
    superusers.delete()
    print("✅ Anciens superusers supprimés")
EOF

echo ""
echo "👑 Création du nouveau superuser complet..."

# Créer le superuser avec tous les privilèges
python manage.py shell << EOF
from accounts.models import User

# Créer le superuser principal
superuser = User.objects.create_user(
    username='SuperAdmin',
    email='superadmin@efintrack.com',
    password='SuperAdmin123!',
    role='ADMIN',  # Rôle ADMIN dans votre système
    first_name='Super',
    last_name='Admin'
)

# Donner tous les privilèges Django
superuser.is_superuser = True      # Accès admin Django complet
superuser.is_staff = True          # Accès interface admin
superuser.is_active = True         # Compte actif
superuser.save()

print("✅ SuperAdmin créé avec succès")
print(f"   Username: {superuser.username}")
print(f"   Email: {superuser.email}")
print(f"   Role: {superuser.role}")
print(f"   Superuser: {superuser.is_superuser}")
print(f"   Staff: {superuser.is_staff}")
print(f"   Actif: {superuser.is_active}")
EOF

echo ""
echo "🔐 Vérification finale..."
python manage.py shell << EOF
from accounts.models import User
from django.contrib.auth import authenticate

# Vérifier le superuser
superuser = User.objects.get(username='SuperAdmin')
print(f"👤 Superuser trouvé: {superuser.username}")
print(f"   Email: {superuser.email}")
print(f"   Role: {superuser.role}")
print(f"   Superuser: {superuser.is_superuser}")
print(f"   Staff: {superuser.is_staff}")

# Tester l'authentification
auth_test = authenticate(username='SuperAdmin', password='SuperAdmin123!')
print(f"   Authentification: {'✅ Succès' if auth_test else '❌ Échec'}")

# Lister tous les utilisateurs
print(f"\n📊 Total utilisateurs: {User.objects.count()}")
print("👥 Liste complète:")
for user in User.objects.all().order_by('username'):
    status = "👑" if user.is_superuser else "👤"
    print(f"   {status} {user.username} ({user.role}) - {'Superuser' if user.is_superuser else 'Normal'}")
EOF

echo ""
echo "🌐 Accès disponibles pour SuperAdmin:"
echo "==================================="
echo "1. 🎯 Interface utilisateur principale:"
echo "   URL: http://187.77.171.80:8000/"
echo "   Login: SuperAdmin"
echo "   Password: SuperAdmin123!"
echo ""
echo "2. 🛠️  Admin Django:"
echo "   URL: http://187.77.171.80:8000/admin/"
echo "   Login: SuperAdmin"
echo "   Password: SuperAdmin123!"
echo ""
echo "3. 🔧 Permissions complètes:"
echo "   ✅ Accès à tous les modèles dans l'admin Django"
echo "   ✅ Création/modification/suppression de toutes les données"
echo "   ✅ Gestion des utilisateurs"
echo "   ✅ Accès à toutes les vues utilisateur"
echo "   ✅ Permissions sur recettes, dépenses, clotures"
echo "   ✅ Gestion des banques, services, natures économiques"

echo ""
echo "🎯 Rôle et capacités:"
echo "===================="
echo "👑 SuperAdmin (ADMIN):"
echo "   • Accès complet à l'interface utilisateur"
echo "   • Accès complet à l'admin Django"
echo "   • Peut créer/modifier/supprimer tout"
echo "   • Peut gérer les autres utilisateurs"
echo "   • Peut clôturer les périodes"
echo "   • Peut gérer toutes les configurations"

echo ""
echo "⚠️  Sécurité:"
echo "==========="
echo "• Changez le mot de passe après la première connexion"
echo "• Utilisez des mots de passe forts en production"
echo "• Limitez l'accès à l'admin Django si nécessaire"

echo ""
echo "✅ Superuser créé avec succès !"
echo "🎊 Vous pouvez maintenant vous connecter avec tous les privilèges !"
