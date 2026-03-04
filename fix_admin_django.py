#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger les problèmes de l'admin Django sur VPS
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles import finders

def diagnose_admin_django():
    """Diagnostic complet de l'admin Django"""
    
    print("🔍 DIAGNOSTIC ADMIN DJANGO - VPS")
    print("=" * 50)
    
    # 1. Vérifier la configuration
    print("\n⚙️  CONFIGURATION ADMIN:")
    print(f"   ADMIN_SITE_TITLE: {getattr(settings, 'ADMIN_SITE_TITLE', 'Non défini')}")
    print(f"   ADMIN_SITE_HEADER: {getattr(settings, 'ADMIN_SITE_HEADER', 'Non défini')}")
    print(f"   ADMIN_INDEX_TITLE: {getattr(settings, 'ADMIN_INDEX_TITLE', 'Non défini')}")
    
    # 2. Vérifier les applications Django
    print(f"\n📦 APPLICATIONS DJANGO ADMIN:")
    admin_apps = ['admin', 'auth', 'contenttypes', 'sessions']
    for app in admin_apps:
        if app in settings.INSTALLED_APPS:
            print(f"   ✅ django.contrib.{app}")
        else:
            print(f"   ❌ django.contrib.{app} MANQUANT")
    
    # 3. Vérifier les fichiers statiques
    print(f"\n📁 FICHIERS STATIQUES ADMIN:")
    
    # Chercher les fichiers statiques de l'admin
    admin_files = []
    for finder in finders.get_finders():
        if hasattr(finder, 'find'):
            try:
                for path, storage in finder.find('admin/css/base.css').items():
                    admin_files.append(path)
            except:
                pass
    
    if admin_files:
        print(f"   ✅ Fichiers admin trouvés: {len(admin_files)}")
        for file_path in admin_files[:3]:  # Limiter l'affichage
            print(f"      - {file_path}")
    else:
        print(f"   ❌ Aucun fichier statique admin trouvé")
    
    # 4. Vérifier les dossiers statiques
    print(f"\n📂 DOSSIERS STATIQUES:")
    static_dirs = [
        settings.STATIC_ROOT,
        settings.MEDIA_ROOT,
    ]
    
    if hasattr(settings, 'STATICFILES_DIRS'):
        static_dirs.extend(settings.STATICFILES_DIRS)
    
    for dir_path in static_dirs:
        if os.path.exists(dir_path):
            file_count = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            dir_count = len([d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))])
            print(f"   ✅ {dir_path} ({file_count} fichiers, {dir_count} dossiers)")
            
            # Vérifier le sous-dossier admin
            admin_path = os.path.join(dir_path, 'admin')
            if os.path.exists(admin_path):
                print(f"      📁 admin/ existe")
            else:
                print(f"      ❌ admin/ manquant")
        else:
            print(f"   ❌ {dir_path} (manquant)")
    
    # 5. Vérifier les URLs
    print(f"\n🌐 CONFIGURATION URLs:")
    from django.urls import get_resolver
    resolver = get_resolver()
    
    admin_patterns = []
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'namespace') and pattern.namespace == 'admin':
            admin_patterns.append(pattern)
    
    if admin_patterns:
        print(f"   ✅ URLs admin trouvées: {len(admin_patterns)}")
    else:
        print(f"   ❌ Aucune URL admin trouvée")
    
    # 6. Vérifier les permissions SuperAdmin
    print(f"\n👤 UTILISATEURS SUPER ADMIN:")
    from django.contrib.auth.models import User
    from accounts.models import User as CustomUser
    
    # Vérifier les deux modèles
    django_users = User.objects.filter(is_superuser=True)
    custom_users = CustomUser.objects.filter(role='SUPER_ADMIN')
    
    print(f"   Django Superusers: {django_users.count()}")
    for user in django_users:
        print(f"      - {user.username} (staff: {user.is_staff})")
    
    print(f"   Custom SUPER_ADMIN: {custom_users.count()}")
    for user in custom_users:
        print(f"      - {user.username} (admin access: {user.peut_acceder_admin_django()})")

def fix_admin_django():
    """Corrige les problèmes courants de l'admin Django"""
    
    print("\n🔧 CORRECTION DES PROBLÈMES ADMIN DJANGO")
    print("=" * 50)
    
    # 1. Recollecter les fichiers statiques
    print("\n📁 RECOLTE DES FICHIERS STATIQUES:")
    os.system("python manage.py collectstatic --noinput --clear")
    print("   ✅ Fichiers statiques recollectés")
    
    # 2. Vérifier les permissions
    print("\n🔒 VÉRIFICATION DES PERMISSIONS:")
    static_root = settings.STATIC_ROOT
    if os.path.exists(static_root):
        os.system(f"chmod -R 755 {static_root}")
        print(f"   ✅ Permissions ajustées pour {static_root}")
    
    # 3. Créer un lien symbolique si nécessaire
    print("\n🔗 VÉRIFICATION DES LIENS SYMBOLIQUES:")
    static_admin_path = os.path.join(settings.STATIC_ROOT, 'admin')
    if not os.path.exists(static_admin_path):
        # Essayer de trouver les fichiers admin dans l'environnement virtuel
        venv_admin_path = None
        if os.path.exists('venv'):
            for root, dirs, files in os.walk('venv'):
                if 'admin' in root and 'css' in dirs:
                    venv_admin_path = root
                    break
        
        if venv_admin_path:
            os.system(f"ln -sf {venv_admin_path} {static_admin_path}")
            print(f"   ✅ Lien symbolique créé: {static_admin_path}")
        else:
            print(f"   ⚠️  Impossible de trouver les fichiers admin")
    
    # 4. Vérifier la configuration du serveur
    print("\n🌐 CONFIGURATION SERVEUR:")
    print("   Pour servir les fichiers statiques en production:")
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"   DEBUG: {settings.DEBUG}")
    
    if not settings.DEBUG:
        print("\n   ⚠️  En mode production, configurez votre serveur web pour servir les fichiers statiques:")
        print("   # Nginx example:")
        print("   location /static/ {")
        print(f"       alias {settings.STATIC_ROOT};")
        print("       expires 1y;")
        print("       add_header Cache-Control \"public, immutable\";")
        print("   }")

if __name__ == "__main__":
    try:
        diagnose_admin_django()
        fix_admin_django()
        
        print(f"\n{'='*50}")
        print("✅ DIAGNOSTIC ET CORRECTION TERMINÉS")
        print("\n🚀 POUR TESTER L'ADMIN:")
        print("   1. Démarrez le serveur: python manage.py runserver 0.0.0.0:8000")
        print("   2. Accédez à: http://187.77.171.80:8000/admin/")
        print("   3. Connectez-vous avec SuperAdmin")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
