#!/bin/bash
# recreate_users.sh - Script pour recréer les utilisateurs sur le VPS

set -e

echo "👥 Recréation des utilisateurs e-FinTrack sur VPS"
echo "=================================================="

# Aller dans le répertoire du projet
cd /var/www/e-fintrack

# Activer l'environnement virtuel
source venv/bin/activate

echo "🗑️  Suppression des utilisateurs existants..."
python manage.py shell << EOF
from accounts.models import User
deleted_count = User.objects.all().delete()[0]
print(f"✅ {deleted_count} utilisateur(s) supprimé(s)")
EOF

echo ""
echo "👤 Création des utilisateurs avec leurs rôles..."

# Créer AdminDaf (ADMIN)
echo "🔧 Création de AdminDaf (ADMIN)..."
python manage.py shell << EOF
from accounts.models import User
admin = User.objects.create_user(
    username='AdminDaf',
    email='admin@efintrack.com',
    password='AdminDaf123!',
    role='ADMIN',
    first_name='Admin',
    last_name='DAF'
)
admin.is_active = True
admin.save()
print("✅ AdminDaf créé avec succès")
EOF

# Créer DirDaf (DG)
echo "🎯 Création de DirDaf (DG)..."
python manage.py shell << EOF
from accounts.models import User
dirdaf = User.objects.create_user(
    username='DirDaf',
    email='dirdaf@efintrack.com',
    password='DirDaf123!',
    role='DG',
    first_name='Directeur',
    last_name='DAF'
)
dirdaf.is_active = True
dirdaf.save()
print("✅ DirDaf créé avec succès")
EOF

# Créer DivDaf (CD_FINANCE)
echo "💰 Création de DivDaf (CD_FINANCE)..."
python manage.py shell << EOF
from accounts.models import User
divdaf = User.objects.create_user(
    username='DivDaf',
    email='divdaf@efintrack.com',
    password='DivDaf123!',
    role='CD_FINANCE',
    first_name='Chef',
    last_name='Division'
)
divdaf.is_active = True
divdaf.save()
print("✅ DivDaf créé avec succès")
EOF

# Créer OpsDaf (OPERATEUR_SAISIE)
echo "⌨️  Création de OpsDaf (OPERATEUR_SAISIE)..."
python manage.py shell << EOF
from accounts.models import User
opsdaf = User.objects.create_user(
    username='OpsDaf',
    email='ops@efintrack.com',
    password='OpsDaf123!',
    role='OPERATEUR_SAISIE',
    first_name='Opérateur',
    last_name='Saisie'
)
opsdaf.is_active = True
opsdaf.save()
print("✅ OpsDaf créé avec succès")
EOF

echo ""
echo "📊 Vérification des utilisateurs créés :"
python manage.py shell << EOF
from accounts.models import User
print("👥 Liste des utilisateurs :")
for user in User.objects.all().order_by('username'):
    print(f"   👤 {user.username} ({user.role}) - {user.email}")
print(f"📊 Total: {User.objects.count()} utilisateur(s)")
EOF

echo ""
echo "🔐 Identifiants de connexion :"
echo "=============================="
echo "👤 AdminDaf    : admin@efintrack.com     | Mot de passe: AdminDaf123!"
echo "👤 DirDaf     : dirdaf@efintrack.com    | Mot de passe: DirDaf123!"
echo "👤 DivDaf     : divdaf@efintrack.com    | Mot de passe: DivDaf123!"
echo "👤 OpsDaf     : ops@efintrack.com       | Mot de passe: OpsDaf123!"
echo ""
echo "🎯 Rôles et permissions :"
echo "   • ADMIN      : Accès complet à tout"
echo "   • DG         : Direction générale"
echo "   • CD_FINANCE : Chef division finance"
echo "   • OPERATEUR_SAISIE : Opérateur de saisie"
echo ""
echo "✅ Utilisateurs recréés avec succès !"
echo "🌐 Vous pouvez maintenant vous connecter à votre site"
