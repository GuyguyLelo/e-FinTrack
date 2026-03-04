#!/usr/bin/env python3
"""
Script de comparaison entre environnement local et VPS
Pour identifier les différences de configuration
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.conf import settings

def compare_environments():
    """Compare les configurations importantes"""
    
    print("🔍 COMPARAISON ENVIRONNEMENT LOCAL vs VPS")
    print("=" * 60)
    
    # Configuration base
    configs = {
        "DEBUG": settings.DEBUG,
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
        "DATABASE_ENGINE": settings.DATABASES['default']['ENGINE'],
        "DATABASE_NAME": settings.DATABASES['default']['NAME'],
        "SECRET_KEY": settings.SECRET_KEY[:20] + "...",
        "LANGUAGE_CODE": settings.LANGUAGE_CODE,
        "TIME_ZONE": settings.TIME_ZONE,
        "USE_TZ": settings.USE_TZ,
        "STATIC_URL": settings.STATIC_URL,
        "MEDIA_URL": settings.MEDIA_URL,
        "AUTH_USER_MODEL": settings.AUTH_USER_MODEL,
        "LOGIN_URL": settings.LOGIN_URL,
        "LOGOUT_REDIRECT_URL": settings.LOGOUT_REDIRECT_URL,
    }
    
    print("\n⚙️  CONFIGURATION DJANGO:")
    for key, value in configs.items():
        print(f"   {key}: {value}")
    
    # Middleware
    print(f"\n🔒 MIDDLEWARE ({len(settings.MIDDLEWARE)}):")
    for i, middleware in enumerate(settings.MIDDLEWARE, 1):
        status = "✅" if "permission" in middleware.lower() or "auth" in middleware.lower() else "  "
        print(f"   {i:2d}. {status} {middleware}")
    
    # Applications installées
    print(f"\n📦 APPLICATIONS INSTALLÉES ({len(settings.INSTALLED_APPS)}):")
    for app in settings.INSTALLED_APPS:
        if app.startswith('django.'):
            prefix = "🔧"
        elif app in ['rest_framework', 'crispy_forms', 'crispy_bootstrap5', 'django_extensions']:
            prefix = "📚"
        else:
            prefix = "🏢"
        print(f"   {prefix} {app}")
    
    # Variables d'environnement
    print(f"\n🌍 VARIABLES D'ENVIRONNEMENT:")
    env_vars = [
        'USE_POSTGRESQL',
        'DB_NAME',
        'DB_USER',
        'DB_HOST',
        'DB_PORT',
        'SECRET_KEY',
        'DEBUG',
        'ALLOWED_HOSTS'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, 'Non défini')
        if 'PASSWORD' in var or 'SECRET' in var:
            value = '***' if value else 'Non défini'
        print(f"   {var}: {value}")

def check_database_content():
    """Vérifie le contenu de la base de données"""
    
    print(f"\n🗄️  CONTENU BASE DE DONNÉES:")
    
    try:
        from accounts.models import User, Service
        
        # Services
        services = Service.objects.all()
        print(f"   🏢 Services: {services.count()}")
        for service in services[:5]:  # Limiter à 5 pour la lisibilité
            print(f"      - {service.nom_service}")
        
        # Utilisateurs
        users = User.objects.all()
        print(f"   👥 Utilisateurs: {users.count()}")
        
        # Répartition par rôle
        roles = {}
        for user in users:
            role = user.get_role_display()
            roles[role] = roles.get(role, 0) + 1
        
        for role, count in roles.items():
            print(f"      - {role}: {count}")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def check_file_system():
    """Vérifie le système de fichiers"""
    
    print(f"\n📁 SYSTÈME DE FICHIERS:")
    
    # Fichiers importants
    files_to_check = [
        'db.sqlite3',
        '.env',
        'requirements.txt',
        'manage.py',
        'check_vps_users.py'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"   ✅ {file_path} ({size} bytes)")
        else:
            print(f"   ❌ {file_path} (manquant)")
    
    # Dossiers importants
    dirs_to_check = [
        'templates',
        'static',
        'media',
        'accounts',
        'venv'
    ]
    
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}/ (existe)")
        else:
            print(f"   ❌ {dir_path}/ (manquant)")

if __name__ == "__main__":
    try:
        compare_environments()
        check_database_content()
        check_file_system()
        
        print(f"\n{'='*60}")
        print("✅ COMPARAISON TERMINÉE")
        print("\n💡 POUR COMPARER AVEC LE VPS:")
        print("1. Copiez ce script sur le VPS")
        print("2. Exécutez-le sur les deux environnements")
        print("3. Comparez les sorties")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
