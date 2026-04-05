from django.core.management.base import BaseCommand
from django.db import transaction
from rbac.models import Role, Permission, RolePermission
from accounts.models import User

class Command(BaseCommand):
    help = 'Synchroniser les rôles RBAC avec les rôles existants des utilisateurs'

    def handle(self, *args, **options):
        self.stdout.write('Début de la synchronisation des rôles...')
        
        # Mapping des rôles existants vers les rôles RBAC
        role_mapping = {
            'SUPER_ADMIN': 'Super Administrateur',
            'ADMIN': 'Administrateur DAF',
            'DG': 'Directeur DAF',  # Utiliser DIR_DAF
            'DF': 'Directeur DAF',   # Utiliser DIR_DAF
            'CD_FINANCE': 'Division DAF',  # Utiliser DIV_DAF
            'OPERATEUR_SAISIE': 'Opération DAF',  # Utiliser OPS_DAF
            'AGENT_PAYEUR': 'Agent Payeur'
        }
        
        # Codes RBAC existants
        rbac_code_mapping = {
            'SUPER_ADMIN': 'SUPER_ADMIN',
            'ADMIN': 'ADMIN_DAF',
            'DG': 'DIR_DAF',
            'DF': 'DIR_DAF',
            'CD_FINANCE': 'DIV_DAF',
            'OPERATEUR_SAISIE': 'OPS_DAF',
            'AGENT_PAYEUR': 'AGENT_PAYEUR'
        }
        
        # Permissions par défaut pour chaque rôle
        default_permissions = {
            'SUPER_ADMIN': ['*'],  # Toutes les permissions
            'ADMIN': ['natures_gestion', 'services_gestion'],
            'DG': ['tableau_bord_voir', 'clotures_voir'],
            'DF': ['tableau_bord_voir', 'clotures_voir'],
            'CD_FINANCE': ['tableau_bord_voir', 'clotures_voir'],
            'OPERATEUR_SAISIE': ['depenses_saisir', 'recettes_saisir', 'etats_voir'],
            'AGENT_PAYEUR': ['paiements_voir', 'paiements_traiter']
        }
        
        with transaction.atomic():
            # Synchroniser les rôles existants
            for user_role_code, role_name in role_mapping.items():
                rbac_code = rbac_code_mapping.get(user_role_code)
                if not rbac_code:
                    self.stdout.write(f'⚠️  Pas de code RBAC pour: {user_role_code}')
                    continue
                
                try:
                    role = Role.objects.get(code=rbac_code)
                    self.stdout.write(f'ℹ️  Rôle existant: {role_name} (code: {rbac_code})')
                    
                    # Attribuer les permissions par défaut
                    permissions_to_add = default_permissions.get(user_role_code, [])
                    if permissions_to_add and permissions_to_add != ['*']:
                        for perm_code in permissions_to_add:
                            try:
                                permission = Permission.objects.get(code=perm_code)
                                RolePermission.objects.get_or_create(
                                    role=role,
                                    permission=permission,
                                    defaults={'attribue_par': None}
                                )
                                self.stdout.write(f'  ✅ Permission ajoutée: {permission.nom}')
                            except Permission.DoesNotExist:
                                self.stdout.write(f'  ⚠️  Permission non trouvée: {perm_code}')
                    elif permissions_to_add == ['*']:
                        # Ajouter toutes les permissions pour Super Admin
                        all_permissions = Permission.objects.filter(est_active=True)
                        for permission in all_permissions:
                            RolePermission.objects.get_or_create(
                                role=role,
                                permission=permission,
                                defaults={'attribue_par': None}
                            )
                        self.stdout.write(f'  ✅ Toutes les permissions ajoutées pour {role_name}')
                        
                except Role.DoesNotExist:
                    self.stdout.write(f'⚠️  Rôle RBAC non trouvé: {rbac_code}')
        
        # Synchroniser les utilisateurs existants
        self.stdout.write('\n🔄 Synchronisation des utilisateurs...')
        for user_role_code, role_name in role_mapping.items():
            rbac_code = rbac_code_mapping.get(user_role_code)
            if not rbac_code:
                continue
                
            try:
                rbac_role = Role.objects.get(code=rbac_code)
                users = User.objects.filter(role=user_role_code)
                for user in users:
                    user.rbac_role = rbac_role
                    user.save(update_fields=['rbac_role'])
                self.stdout.write(f'  ✅ {users.count()} utilisateur(s) synchronisé(s) avec {role_name}')
            except Role.DoesNotExist:
                self.stdout.write(f'  ⚠️  Rôle RBAC non trouvé pour: {rbac_code}')
        
        # Afficher le résumé
        self.stdout.write('\n📊 Résumé de la synchronisation:')
        self.stdout.write(f'   Rôles créés/mis à jour: {len(role_mapping)}')
        self.stdout.write(f'   Permissions totales: {Permission.objects.count()}')
        self.stdout.write(f'   Rôles-Permissions créés: {RolePermission.objects.count()}')
        
        # Afficher les utilisateurs par rôle
        self.stdout.write('\n👥 Utilisateurs par rôle:')
        for user_role_code, role_name in role_mapping.items():
            try:
                role = Role.objects.get(code=user_role_code)
                user_count = User.objects.filter(role=user_role_code).count()
                self.stdout.write(f'   {role_name}: {user_count} utilisateur(s)')
            except Role.DoesNotExist:
                self.stdout.write(f'   {role_name}: Rôle non trouvé')
        
        self.stdout.write('\n✨ Synchronisation terminée avec succès!')

    def get_role_color(self, role_code):
        """Définir la couleur pour chaque rôle"""
        colors = {
            'SUPER_ADMIN': '#dc3545',  # Rouge
            'ADMIN': '#28a745',        # Vert
            'DG': '#007bff',           # Bleu
            'DF': '#6f42c1',           # Violet
            'CD_FINANCE': '#fd7e14',   # Orange
            'OPERATEUR_SAISIE': '#20c997', # Turquoise
            'AGENT_PAYEUR': '#6c757d'  # Gris
        }
        return colors.get(role_code, '#6c757d')

    def get_role_icon(self, role_code):
        """Définir l'icône pour chaque rôle"""
        icons = {
            'SUPER_ADMIN': 'bi-shield-fill-check',
            'ADMIN': 'bi-gear-fill',
            'DG': 'bi-person-badge-fill',
            'DF': 'bi-graph-up-arrow',
            'CD_FINANCE': 'bi-calculator-fill',
            'OPERATEUR_SAISIE': 'bi-pencil-square',
            'AGENT_PAYEUR': 'bi-cash-coin'
        }
        return icons.get(role_code, 'bi-person')
