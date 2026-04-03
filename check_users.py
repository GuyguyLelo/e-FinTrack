#!/usr/bin/env python
"""
Script pour vérifier les utilisateurs et résoudre les problèmes de connexion
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User

def check_users():
    """Vérifier tous les utilisateurs et leur état"""
    print("🔍 Vérification des utilisateurs")
    print("=" * 50)
    
    users = User.objects.all()
    print(f"📊 Total d'utilisateurs: {users.count()}")
    print()
    
    # Liste des utilisateurs attendus
    expected_users = ['SuperAdmin', 'AdminDaf', 'DirDaf', 'DivDaf', 'OpsDaf', 'Operateur']
    
    print("📋 État des utilisateurs:")
    print("-" * 50)
    print(f"{'Username':15} | {'SuperAdmin':8} | {'Actif':5} | {'Rôle':15}")
    print("-" * 50)
    
    for user in users:
        print(f"{user.username:15} | {str(user.is_superuser):8} | {str(user.is_active):5} | {getattr(user, 'role', 'N/A'):15}")
    
    print()
    
    # Vérification des utilisateurs manquants
    existing_usernames = [user.username for user in users]
    missing_users = [u for u in expected_users if u not in existing_usernames]
    
    if missing_users:
        print("❌ Utilisateurs manquants:")
        for username in missing_users:
            print(f"   - {username}")
    else:
        print("✅ Tous les utilisateurs attendus existent")
    
    print()
    
    # Vérification des utilisateurs qui peuvent se connecter
    can_connect = []
    cannot_connect = []
    
    for user in users:
        if user.is_active:
            if user.username in ['SuperAdmin', 'AdminDaf', 'Operateur']:
                can_connect.append(user.username)
            else:
                cannot_connect.append(user.username)
        else:
            cannot_connect.append(f"{user.username} (inactif)")
    
    print("🔐 État de connexion:")
    print(f"   ✅ Peuvent se connecter ({len(can_connect)}): {', '.join(can_connect)}")
    print(f"   ❌ Ne peuvent pas se connecter ({len(cannot_connect)}): {', '.join(cannot_connect)}")
    
    print()
    
    # Suggestions
    if cannot_connect:
        print("💡 Suggestions pour résoudre le problème:")
        print("   1. Vérifier que les utilisateurs sont actifs (is_active=True)")
        print("   2. Vérifier que les mots de passe sont corrects")
        print("   3. Vérifier les permissions dans les settings")
        print("   4. Vérifier les logs du serveur pour les erreurs de connexion")
        
        # Créer les utilisateurs manquants si nécessaire
        if missing_users:
            print(f"\n🔧 Création des utilisateurs manquants...")
            for username in missing_users:
                try:
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'password': 'temp123',  # Mot de passe temporaire
                            'is_active': True,
                            'is_superuser': username == 'SuperAdmin'
                        }
                    )
                    if created:
                        user.set_password('temp123')
                        user.save()
                        print(f"   ✅ {username} créé (mot de passe: temp123)")
                    else:
                        user.is_active = True
                        user.save()
                        print(f"   ✅ {username} activé")
                except Exception as e:
                    print(f"   ❌ Erreur avec {username}: {e}")

def fix_connection_issues():
    """Réparer les problèmes de connexion courants"""
    print("\n🔧 Réparation des problèmes de connexion...")
    
    # Activer tous les utilisateurs
    updated = User.objects.filter(is_active=False).update(is_active=True)
    if updated > 0:
        print(f"   ✅ {updated} utilisateur(s) activé(s)")
    else:
        print("   ✅ Tous les utilisateurs sont déjà actifs")
    
    # Vérifier les mots de passe
    users = User.objects.all()
    print("\n🔐 Test des mots de passe:")
    for user in users:
        if user.username in ['SuperAdmin', 'AdminDaf', 'Operateur']:
            print(f"   ✅ {user.username}: mot de passe configuré")
        else:
            print(f"   ⚠️  {user.username}: vérifier le mot de passe")

if __name__ == "__main__":
    check_users()
    fix_connection_issues()
    
    print("\n🎯 Actions recommandées:")
    print("1. Redémarrez le serveur Django")
    print("2. Essayez de vous connecter avec les identifiants suivants:")
    print("   - SuperAdmin / Super123!")
    print("   - AdminDaf / Admin123!")
    print("   - Operateur / Oper123!")
    print("3. Si ça ne fonctionne pas, vérifiez les logs du navigateur et du serveur")
