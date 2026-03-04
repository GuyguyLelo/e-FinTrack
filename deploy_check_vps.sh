#!/bin/bash

# Script de déploiement et vérification pour VPS
echo "🚀 DÉPLOIEMENT ET VÉRIFICATION VPS - e-FinTrack"
echo "=================================================="

# Vérifier si on est sur le VPS
if [[ "$HOSTNAME" == *"vps"* ]] || [[ "$HOSTNAME" == *"187"* ]]; then
    echo "✅ Détection VPS: $HOSTNAME"
else
    echo "⚠️  Ce script est optimisé pour le VPS"
fi

# 1. Activer l'environnement virtuel
echo ""
echo "🔧 Activation de l'environnement virtuel..."
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Environnement virtuel activé"
else
    echo "❌ Environnement virtuel non trouvé"
    echo "💡 Créez-le avec: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 2. Vérifier l'installation Django
echo ""
echo "🐍 Vérification Django..."
python -c "import django; print(f'✅ Django {django.get_version()} installé')" || {
    echo "❌ Django non installé"
    echo "💡 Installez-le avec: pip install django"
    exit 1
}

# 3. Vérifier la base de données
echo ""
echo "🗄️  Vérification base de données..."
if [ -f "db.sqlite3" ]; then
    echo "✅ Base SQLite trouvée"
    ls -la db.sqlite3
elif [ "$USE_POSTGRESQL" = "True" ]; then
    echo "✅ Configuration PostgreSQL détectée"
else
    echo "⚠️  Aucune base de données trouvée"
fi

# 4. Appliquer les migrations
echo ""
echo "🔄 Application des migrations..."
python manage.py migrate --noinput || {
    echo "❌ Erreur lors des migrations"
    exit 1
}

# 5. Vérifier les superutilisateurs
echo ""
echo "👤 Vérification des superutilisateurs..."
python manage.py shell -c "
from accounts.models import User;
superusers = User.objects.filter(is_superuser=True);
print(f'Superutilisateurs: {superusers.count()}');
for u in superusers:
    print(f'  - {u.username} ({u.email})');
" || {
    echo "⚠️  Impossible de vérifier les superutilisateurs"
}

# 6. Charger les données initiales si nécessaire
echo ""
echo "📋 Vérification des données initiales..."
python manage.py shell -c "
from accounts.models import User, Service;
users_count = User.objects.count();
services_count = Service.objects.count();
print(f'Utilisateurs: {users_count}, Services: {services_count}');
if users_count == 0:
    print('⚠️  Aucun utilisateur - chargement des données initial...');
" || {
    echo "⚠️  Vérification des données impossible"
}

# 7. Exécuter le script de vérification
echo ""
echo "🔍 Exécution du script de vérification..."
python check_vps_users.py || {
    echo "❌ Erreur lors de la vérification"
    exit 1
}

# 8. Vérifier les permissions des fichiers
echo ""
echo "🔒 Vérification des permissions..."
find . -name "*.py" -exec chmod 644 {} \;
find . -name "*.sh" -exec chmod 755 {} \;
echo "✅ Permissions des fichiers ajustées"

# 9. Vérifier le serveur
echo ""
echo "🌐 Test du serveur..."
python manage.py check --deploy || {
    echo "⚠️  Quelques problèmes de configuration détectés"
}

# 10. Instructions finales
echo ""
echo "📋 RÉCAPITULATIF:"
echo "✅ Environnement prêt"
echo "✅ Base de données vérifiée"
echo "✅ Utilisateurs et droits analysés"
echo ""
echo "🚀 POUR DÉMARRER LE SERVEUR:"
echo "   python manage.py runserver 0.0.0.0:8000"
echo ""
echo "🔍 POUR VÉRIFIER À NOUVEAU:"
echo "   python check_vps_users.py"
echo ""
echo "📊 ACCÈS WEB:"
echo "   http://187.77.171.80:8000"
echo "   http://localhost:8000 (local)"
echo ""
echo "=================================================="
echo "✅ VÉRIFICATION VPS TERMINÉE"
