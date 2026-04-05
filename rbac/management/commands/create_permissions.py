"""
Commande pour créer les permissions de base
"""
from django.core.management.base import BaseCommand
from rbac.models import Permission, Role, RolePermission


class Command(BaseCommand):
    help = 'Crée les permissions de base pour le système'

    def handle(self, *args, **options):
        print("🔧 Création des permissions de base...")
        
        # Définition des permissions
        permissions_data = [
            # Tableau de bord
            {'nom': 'Voir tableau de bord', 'code': 'voir_tableau_bord', 'module': 'tableau_bord', 
             'description': 'Accéder au tableau de bord principal'},
            {'nom': 'Voir tableau de bord feuille', 'code': 'voir_tableau_bord_feuille', 'module': 'tableau_bord',
             'description': 'Accéder au tableau de bord feuille'},
            
            # Demandes
            {'nom': 'Voir demandes', 'code': 'voir_demandes', 'module': 'demandes',
             'description': 'Voir la liste des demandes'},
            {'nom': 'Créer demandes', 'code': 'creer_demandes', 'module': 'demandes',
             'description': 'Créer de nouvelles demandes'},
            {'nom': 'Valider demandes', 'code': 'valider_demandes', 'module': 'demandes',
             'description': 'Valider les demandes'},
            {'nom': 'Modifier demandes', 'code': 'modifier_demandes', 'module': 'demandes',
             'description': 'Modifier les demandes existantes'},
            {'nom': 'Supprimer demandes', 'code': 'supprimer_demandes', 'module': 'demandes',
             'description': 'Supprimer des demandes'},
            
            # Paiements
            {'nom': 'Voir paiements', 'code': 'voir_paiements', 'module': 'paiements',
             'description': 'Voir la liste des paiements'},
            {'nom': 'Créer paiements', 'code': 'creer_paiements', 'module': 'paiements',
             'description': 'Créer de nouveaux paiements'},
            {'nom': 'Effectuer paiements', 'code': 'effectuer_paiements', 'module': 'paiements',
             'description': 'Effectuer des paiements'},
            {'nom': 'Modifier paiements', 'code': 'modifier_paiements', 'module': 'paiements',
             'description': 'Modifier les paiements existants'},
            
            # Recettes
            {'nom': 'Voir recettes', 'code': 'voir_recettes', 'module': 'recettes',
             'description': 'Voir la liste des recettes'},
            {'nom': 'Créer recettes', 'code': 'creer_recettes', 'module': 'recettes',
             'description': 'Créer de nouvelles recettes'},
            {'nom': 'Modifier recettes', 'code': 'modifier_recettes', 'module': 'recettes',
             'description': 'Modifier les recettes existantes'},
            
            # Relevés
            {'nom': 'Voir relevés', 'code': 'voir_releves', 'module': 'releves',
             'description': 'Voir la liste des relevés'},
            {'nom': 'Créer relevés', 'code': 'creer_releves', 'module': 'releves',
             'description': 'Créer de nouveaux relevés'},
            {'nom': 'Valider relevés', 'code': 'valider_releves', 'module': 'releves',
             'description': 'Valider les relevés'},
            
            # États
            {'nom': 'Voir états', 'code': 'voir_etats', 'module': 'etats',
             'description': 'Voir la liste des états'},
            {'nom': 'Créer états', 'code': 'creer_etats', 'module': 'etats',
             'description': 'Créer de nouveaux états'},
            {'nom': 'Générer états', 'code': 'generer_etats', 'module': 'etats',
             'description': 'Générer des états'},
            
            # Banques
            {'nom': 'Voir banques', 'code': 'voir_banques', 'module': 'banques',
             'description': 'Voir la liste des banques'},
            {'nom': 'Créer banques', 'code': 'creer_banques', 'module': 'banques',
             'description': 'Créer de nouvelles banques'},
            {'nom': 'Modifier banques', 'code': 'modifier_banques', 'module': 'banques',
             'description': 'Modifier les banques existantes'},
            
            # Clôtures
            {'nom': 'Voir clôtures', 'code': 'voir_clotures', 'module': 'clotures',
             'description': 'Voir la liste des clôtures'},
            {'nom': 'Effectuer clôtures', 'code': 'effectuer_clotures', 'module': 'clotures',
             'description': 'Effectuer des clôtures'},
            {'nom': 'Rouvrir clôtures', 'code': 'rouvrir_clotures', 'module': 'clotures',
             'description': 'Rouvrir des clôtures'},
            
            # Utilisateurs
            {'nom': 'Voir utilisateurs', 'code': 'voir_utilisateurs', 'module': 'utilisateurs',
             'description': 'Voir la liste des utilisateurs'},
            {'nom': 'Créer utilisateurs', 'code': 'creer_utilisateurs', 'module': 'utilisateurs',
             'description': 'Créer de nouveaux utilisateurs'},
            {'nom': 'Modifier utilisateurs', 'code': 'modifier_utilisateurs', 'module': 'utilisateurs',
             'description': 'Modifier les utilisateurs existants'},
            {'nom': 'Supprimer utilisateurs', 'code': 'supprimer_utilisateurs', 'module': 'utilisateurs',
             'description': 'Supprimer des utilisateurs'},
            
            # Permissions
            {'nom': 'Voir rôles', 'code': 'voir_roles', 'module': 'permissions',
             'description': 'Voir la liste des rôles'},
            {'nom': 'Créer rôles', 'code': 'creer_roles', 'module': 'permissions',
             'description': 'Créer de nouveaux rôles'},
            {'nom': 'Modifier rôles', 'code': 'modifier_roles', 'module': 'permissions',
             'description': 'Modifier les rôles existants'},
            {'nom': 'Supprimer rôles', 'code': 'supprimer_roles', 'module': 'permissions',
             'description': 'Supprimer des rôles'},
            {'nom': 'Gérer permissions', 'code': 'gerer_permissions', 'module': 'permissions',
             'description': 'Gérer les permissions des rôles'},
        ]
        
        # Créer les permissions
        permissions_creates = 0
        for perm_data in permissions_data:
            permission, created = Permission.objects.get_or_create(
                code=perm_data['code'],
                defaults=perm_data
            )
            if created:
                permissions_creates += 1
                self.stdout.write(f"✅ Permission créée: {permission.nom}")
        
        print(f"\n📊 {permissions_creates} permissions créées au total")
        
        # Créer les rôles de base
        print("\n🎯 Création des rôles de base...")
        
        roles_data = [
            {
                'nom': 'Super Administrateur',
                'code': 'SUPER_ADMIN',
                'description': 'Accès complet à toutes les fonctionnalités',
                'couleur': '#dc3545',
                'icone': 'bi-shield-fill',
                'est_systeme': True,
                'permissions_codes': [
                    'voir_tableau_bord', 'voir_tableau_bord_feuille',
                    'voir_demandes', 'creer_demandes', 'valider_demandes', 'modifier_demandes', 'supprimer_demandes',
                    'voir_paiements', 'creer_paiements', 'effectuer_paiements', 'modifier_paiements',
                    'voir_recettes', 'creer_recettes', 'modifier_recettes',
                    'voir_releves', 'creer_releves', 'valider_releves',
                    'voir_etats', 'creer_etats', 'generer_etats',
                    'voir_banques', 'creer_banques', 'modifier_banques',
                    'voir_clotures', 'effectuer_clotures', 'rouvrir_clotures',
                    'voir_utilisateurs', 'creer_utilisateurs', 'modifier_utilisateurs', 'supprimer_utilisateurs',
                    'voir_roles', 'creer_roles', 'modifier_roles', 'supprimer_roles', 'gerer_permissions',
                ]
            },
            {
                'nom': 'Administrateur DAF',
                'code': 'ADMIN_DAF',
                'description': 'Gestion administrative de la DAF',
                'couleur': '#0d6efd',
                'icone': 'bi-person-badge',
                'est_systeme': True,
                'permissions_codes': [
                    'voir_tableau_bord', 'voir_tableau_bord_feuille',
                    'voir_demandes', 'creer_demandes', 'modifier_demandes',
                    'voir_paiements', 'creer_paiements', 'modifier_paiements',
                    'voir_recettes', 'creer_recettes', 'modifier_recettes',
                    'voir_releves', 'creer_releves',
                    'voir_etats', 'creer_etats', 'generer_etats',
                    'voir_banques', 'modifier_banques',
                    'voir_clotures', 'effectuer_clotures',
                    'voir_utilisateurs',
                ]
            },
            {
                'nom': 'Directeur DAF',
                'code': 'DIR_DAF',
                'description': 'Direction des opérations DAF',
                'couleur': '#198754',
                'icone': 'bi-briefcase',
                'est_systeme': True,
                'permissions_codes': [
                    'voir_tableau_bord_feuille',
                    'voir_demandes', 'creer_demandes', 'modifier_demandes',
                    'voir_paiements', 'creer_paiements', 'modifier_paiements',
                    'voir_recettes', 'creer_recettes', 'modifier_recettes',
                    'voir_releves', 'creer_releves',
                    'voir_etats', 'creer_etats', 'generer_etats',
                    'voir_banques',
                    'voir_clotures', 'effectuer_clotures',
                ]
            },
            {
                'nom': 'Division DAF',
                'code': 'DIV_DAF',
                'description': 'Division opérationnelle DAF',
                'couleur': '#6f42c1',
                'icone': 'bi-diagram-3',
                'est_systeme': True,
                'permissions_codes': [
                    'voir_tableau_bord_feuille',
                    'voir_demandes', 'creer_demandes', 'modifier_demandes',
                    'voir_paiements', 'creer_paiements', 'modifier_paiements',
                    'voir_recettes', 'creer_recettes', 'modifier_recettes',
                    'voir_releves', 'creer_releves',
                    'voir_etats', 'creer_etats', 'generer_etats',
                    'voir_banques',
                    'voir_clotures',
                ]
            },
            {
                'nom': 'Opération DAF',
                'code': 'OPS_DAF',
                'description': 'Opérations quotidiennes DAF',
                'couleur': '#20c997',
                'icone': 'bi-gear',
                'est_systeme': True,
                'permissions_codes': [
                    'voir_tableau_bord_feuille',
                    'voir_demandes', 'creer_demandes', 'modifier_demandes',
                    'voir_paiements', 'creer_paiements', 'modifier_paiements',
                    'voir_recettes', 'creer_recettes', 'modifier_recettes',
                    'voir_releves', 'creer_releves',
                    'voir_etats', 'creer_etats', 'generer_etats',
                ]
            },
            {
                'nom': 'Opérateur',
                'code': 'OPERATEUR',
                'description': 'Opérateur de saisie',
                'couleur': '#6c757d',
                'icone': 'bi-person',
                'est_systeme': True,
                'permissions_codes': [
                    'voir_demandes', 'creer_demandes', 'modifier_demandes',
                    'voir_paiements', 'creer_paiements', 'modifier_paiements',
                    'voir_recettes', 'creer_recettes', 'modifier_recettes',
                    'voir_releves', 'creer_releves',
                    'voir_etats', 'creer_etats', 'generer_etats',
                ]
            },
        ]
        
        # Créer les rôles et leurs permissions
        roles_creates = 0
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                code=role_data['code'],
                defaults={k: v for k, v in role_data.items() if k != 'permissions_codes'}
            )
            
            if created:
                roles_creates += 1
                self.stdout.write(f"✅ Rôle créé: {role.nom}")
            
            # Ajouter les permissions au rôle
            for perm_code in role_data['permissions_codes']:
                try:
                    permission = Permission.objects.get(code=perm_code)
                    RolePermission.objects.get_or_create(role=role, permission=permission)
                except Permission.DoesNotExist:
                    self.stdout.write(f"⚠️  Permission non trouvée: {perm_code}")
        
        print(f"\n📊 {roles_creates} rôles créés au total")
        print("\n🎉 Système de permissions initialisé avec succès !")
