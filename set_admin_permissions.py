#!/usr/bin/env python
import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

def setup_admin_permissions():
    """Configure les permissions pour l'utilisateur admin"""
    
    try:
        # Récupérer l'utilisateur admin
        admin = User.objects.get(username='admin')
        print(f'Configuration des permissions pour {admin.username} (role: {admin.role})')
        
        # Vider les permissions existantes
        admin.user_permissions.clear()
        
        # Donner les permissions de vue pour tous les modèles
        permissions_added = 0
        for content_type in ContentType.objects.all():
            # Permission de vue
            try:
                view_perm = Permission.objects.get(
                    content_type=content_type,
                    codename=f'view_{content_type.model}'
                )
                admin.user_permissions.add(view_perm)
                permissions_added += 1
                print(f'✅ Ajouté permission view_{content_type.model}')
            except Permission.DoesNotExist:
                pass
            
            # Permission de changement pour les modèles autorisés
            if content_type.model in ['service', 'banque', 'comptebancaire', 'user', 'natureeconomique']:
                try:
                    change_perm = Permission.objects.get(
                        content_type=content_type,
                        codename=f'change_{content_type.model}'
                    )
                    admin.user_permissions.add(change_perm)
                    permissions_added += 1
                    print(f'✅ Ajouté permission change_{content_type.model}')
                except Permission.DoesNotExist:
                    pass
            
            # Permission d'ajout pour les modèles autorisés
            if content_type.model in ['service', 'banque', 'comptebancaire', 'user', 'natureeconomique']:
                try:
                    add_perm = Permission.objects.get(
                        content_type=content_type,
                        codename=f'add_{content_type.model}'
                    )
                    admin.user_permissions.add(add_perm)
                    permissions_added += 1
                    print(f'✅ Ajouté permission add_{content_type.model}')
                except Permission.DoesNotExist:
                    pass
        
        print(f'\n✅ Total permissions ajoutées: {permissions_added}')
        print(f'✅ Permissions finales pour admin: {admin.user_permissions.count()}')
        
        return True
        
    except User.DoesNotExist:
        print('❌ Utilisateur admin non trouvé')
        return False
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return False

if __name__ == '__main__':
    setup_admin_permissions()
