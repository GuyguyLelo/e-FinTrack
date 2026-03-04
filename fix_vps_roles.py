#!/usr/bin/env python3
"""
Script pour corriger les rôles sur le VPS
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User, Service

def fix_vps_roles():
    """Correction des rôles et ajout des services manquants"""
    
    print("🔧 CORRECTION DES RÔLES ET SERVICES - VPS")
    print("=" * 50)
    
    # 1. Créer les services manquants
    print("\n📋 CRÉATION DES SERVICES:")
    services_data = [
        {"nom_service": "Direction Générale", "description": "Direction Générale de la DGRAD"},
        {"nom_service": "Service Financier", "description": "Service de gestion financière"},
        {"nom_service": "Service Comptable", "description": "Service de comptabilité"},
        {"nom_service": "Service Audit", "description": "Service d'audit interne"},
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            nom_service=service_data["nom_service"],
            defaults={"description": service_data["description"], "actif": True}
        )
        if created:
            print(f"   ✅ Service créé: {service.nom_service}")
        else:
            print(f"   ℹ️  Service existant: {service.nom_service}")
    
    # 2. Corriger les rôles des utilisateurs
    print("\n👤 CORRECTION DES RÔLES:")
    
    corrections = [
        ("AdminDaf", "ADMIN", "Service Financier"),
        ("SuperAdmin", "SUPER_ADMIN", "Direction Générale"),
        ("DirDaf", "DG", "Direction Générale"),
        ("DivDaf", "CD_FINANCE", "Service Financier"),
        ("OpsDaf", "OPERATEUR_SAISIE", "Service Comptable"),
    ]
    
    for username, role, service_name in corrections:
        try:
            user = User.objects.get(username=username)
            old_role = user.get_role_display()
            
            # Mettre à jour le rôle
            user.role = role
            
            # Assigner le service
            try:
                service = Service.objects.get(nom_service=service_name)
                user.service = service
            except Service.DoesNotExist:
                print(f"   ⚠️  Service '{service_name}' non trouvé pour {username}")
            
            user.save()
            
            print(f"   ✅ {username}: {old_role} → {user.get_role_display()} ({service_name})")
            
        except User.DoesNotExist:
            print(f"   ❌ Utilisateur {username} non trouvé")
    
    # 3. Ajouter l'utilisateur manquant
    print("\n➕ AJOUT UTILISATEUR MANQUANT:")
    try:
        if not User.objects.filter(username="TestUser").exists():
            test_user = User.objects.create_user(
                username="TestUser",
                email="testuser@efintrack.com",
                password="testuser123",
                role="DG",
                actif=True
            )
            # Assigner le service
            try:
                service = Service.objects.get(nom_service="Direction Générale")
                test_user.service = service
                test_user.save()
            except Service.DoesNotExist:
                pass
            
            print(f"   ✅ TestUser créé (DG)")
        else:
            print(f"   ℹ️  TestUser existe déjà")
    except Exception as e:
        print(f"   ❌ Erreur création TestUser: {e}")
    
    # 4. Vérification finale
    print("\n📊 VÉRIFICATION FINALE:")
    users = User.objects.all()
    for user in users:
        service_name = user.service.nom_service if user.service else "Non assigné"
        print(f"   👤 {user.username} ({user.get_role_display()}) - {service_name}")
    
    print(f"\n✅ CORRECTION TERMINÉE")
    print(f"   Utilisateurs: {User.objects.count()}")
    print(f"   Services: {Service.objects.count()}")

if __name__ == "__main__":
    try:
        fix_vps_roles()
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
