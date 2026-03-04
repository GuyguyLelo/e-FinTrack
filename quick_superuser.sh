#!/bin/bash
# quick_superuser.sh - Version rapide pour créer un superuser

set -e

echo "🚀 Création Rapide Superuser Django"
echo "================================="

cd /var/www/e-fintrack
source venv/bin/activate

# Script Python pour créer le superuser
python manage.py shell << 'EOF'
from accounts.models import User

# Supprimer l'ancien superuser s'il existe
try:
    old_superuser = User.objects.get(username='SuperAdmin')
    old_superuser.delete()
    print("🗑️  Ancien SuperAdmin supprimé")
except User.DoesNotExist:
    print("ℹ️  Aucun ancien SuperAdmin trouvé")

# Créer le nouveau superuser
superuser = User.objects.create_user(
    username='SuperAdmin',
    email='superadmin@efintrack.com',
    password='SuperAdmin123!',
    role='ADMIN',
    first_name='Super',
    last_name='Admin'
)

# Donner tous les privilèges
superuser.is_superuser = True
superuser.is_staff = True
superuser.is_active = True
superuser.save()

print("✅ SuperAdmin créé avec succès")
print(f"   Username: {superuser.username}")
print(f"   Email: {superuser.email}")
print(f"   Role: {superuser.role}")
print(f"   Superuser: {superuser.is_superuser}")
print(f"   Staff: {superuser.is_staff}")

# Vérification finale
print(f"\n📊 Total utilisateurs: {User.objects.count()}")
print("👥 Liste des utilisateurs:")
for user in User.objects.all().order_by('username'):
    crown = "👑" if user.is_superuser else "👤"
    print(f"   {crown} {user.username} ({user.role})")
EOF

echo ""
echo "🔐 Identifiants de connexion:"
echo "============================"
echo "👑 SuperAdmin : superadmin@efintrack.com"
echo "🔑 Mot de passe: SuperAdmin123!"
echo ""
echo "🌐 Accès:"
echo "========"
echo "• Interface utilisateur: http://187.77.171.80:8000/"
echo "• Admin Django: http://187.77.171.80:8000/admin/"
echo ""
echo "✅ Superuser prêt à l'utilisation !"
