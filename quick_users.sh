#!/bin/bash
# quick_users.sh - Version rapide pour recréer les utilisateurs

set -e

echo "🚀 Création rapide des utilisateurs e-FinTrack"
echo "============================================="

cd /var/www/e-fintrack
source venv/bin/activate

# Script Python pour créer tous les utilisateurs
python manage.py shell << 'EOF'
from accounts.models import User

# Supprimer tous les utilisateurs existants
User.objects.all().delete()
print("🗑️  Anciens utilisateurs supprimés")

# Créer les nouveaux utilisateurs avec leurs rôles
utilisateurs = [
    {
        'username': 'AdminDaf',
        'email': 'admin@efintrack.com',
        'password': 'AdminDaf123!',
        'role': 'ADMIN',
        'first_name': 'Admin',
        'last_name': 'DAF'
    },
    {
        'username': 'DirDaf',
        'email': 'dirdaf@efintrack.com',
        'password': 'DirDaf123!',
        'role': 'DG',
        'first_name': 'Directeur',
        'last_name': 'DAF'
    },
    {
        'username': 'DivDaf',
        'email': 'divdaf@efintrack.com',
        'password': 'DivDaf123!',
        'role': 'CD_FINANCE',
        'first_name': 'Chef',
        'last_name': 'Division'
    },
    {
        'username': 'OpsDaf',
        'email': 'ops@efintrack.com',
        'password': 'OpsDaf123!',
        'role': 'OPERATEUR_SAISIE',
        'first_name': 'Opérateur',
        'last_name': 'Saisie'
    }
]

# Créer chaque utilisateur
for user_data in utilisateurs:
    user = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        role=user_data['role'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )
    user.is_active = True
    user.save()
    print(f"✅ {user_data['username']} ({user_data['role']}) créé")

print(f"\n📊 Total: {User.objects.count()} utilisateurs créés")
print("\n👥 Liste des utilisateurs:")
for user in User.objects.all().order_by('username'):
    print(f"   👤 {user.username} - {user.role} - {user.email}")
EOF

echo ""
echo "🔐 Identifiants de connexion :"
echo "=============================="
echo "👤 AdminDaf    : admin@efintrack.com     | Mot de passe: AdminDaf123!"
echo "👤 DirDaf     : dirdaf@efintrack.com    | Mot de passe: DirDaf123!"
echo "👤 DivDaf     : divdaf@efintrack.com    | Mot de passe: DivDaf123!"
echo "👤 OpsDaf     : ops@efintrack.com       | Mot de passe: OpsDaf123!"
echo ""
echo "✅ Tous les utilisateurs ont été créés avec succès !"
