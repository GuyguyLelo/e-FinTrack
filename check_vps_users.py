#!/usr/bin/env python3
"""
Script de vérification des utilisateurs et droits sur VPS
À exécuter sur le VPS pour comparer avec l'environnement local
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User, Service

def check_users_and_rights():
    """Vérification complète des utilisateurs et leurs droits"""
    
    print("="*80)
    print("🔍 VÉRIFICATION DES UTILISATEURS ET DROITS - VPS")
    print("="*80)
    
    # 1. Vérification des services disponibles
    print("\n📋 SERVICES DISPONIBLES:")
    services = Service.objects.all()
    if services:
        for service in services:
            print(f"   🏢 {service.nom_service} (ID: {service.id}) - {'✅ Actif' if service.actif else '❌ Inactif'}")
    else:
        print("   ⚠️  Aucun service trouvé dans la base de données")
    
    # 2. Vérification des utilisateurs
    print(f"\n👥 UTILISATEURS TROUVÉS: {User.objects.count()}")
    users = User.objects.all()
    
    if not users:
        print("   ⚠️  Aucun utilisateur trouvé!")
        print("\n💡 SUGGESTION: Exécutez ces commandes sur le VPS:")
        print("   python manage.py loaddata accounts/fixtures/initial_data.json")
        print("   python manage.py createsuperuser")
        return
    
    # 3. Analyse détaillée de chaque utilisateur
    for u in users:
        print(f"\n{'='*60}")
        print(f"👤 {u.username} ({u.get_role_display()})")
        print(f"   ✅ Actif: {u.actif}")
        print(f"   🏢 Service: {u.service.nom_service if u.service else 'Non assigné'}")
        print(f"   📧 Email: {u.email}")
        print(f"   📅 Créé le: {u.date_creation.strftime('%d/%m/%Y %H:%M') if u.date_creation else 'N/A'}")
        
        # Vérification des droits
        print("\n   📋 DROITS D'ACCÈS:")
        
        droits = [
            ('Tableau de bord', u.peut_voir_tableau_bord()),
            ('Créer entités de base', u.peut_creer_entites_base()),
            ('Voir tout sans modification', u.peut_voir_tout_sans_modification()),
            ('Valider demandes', u.peut_valider_demandes()),
            ('Valider dépenses', u.peut_valider_depense()),
            ('Effectuer paiements', u.peut_effectuer_paiements()),
            ('Voir paiements', u.peut_voir_paiements()),
            ('Créer relevés', u.peut_creer_releves()),
            ('Consulter dépenses', u.peut_consulter_depenses()),
            ('Voir menu dépenses', u.peut_voir_menu_depenses()),
            ('Créer états', u.peut_creer_etats()),
            ('Saisir demandes/recettes', u.peut_saisir_demandes_recettes()),
            ('Accès admin Django', u.peut_acceder_admin_django()),
            ('Voir menu demandes', u.peut_voir_menu_demandes()),
            ('Voir menu paiements', u.peut_voir_menu_paiements()),
            ('Voir menu recettes', u.peut_voir_menu_recettes()),
            ('Voir menu états', u.peut_voir_menu_etats()),
            ('Voir menu banques', u.peut_voir_menu_banques()),
            ('Ajouter nature économique', u.peut_ajouter_nature_economique()),
            ('Ajouter recette/dépense', u.peut_ajouter_recette_depense()),
            ('Générer états', u.peut_generer_etats()),
        ]
        
        for droit, acces in droits:
            icon = '✅' if acces else '❌'
            print(f"   {icon} {droit}")
    
    # 4. Résumé par rôle
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ PAR RÔLE:")
    
    roles_count = {}
    for user in users:
        role = user.get_role_display()
        if role not in roles_count:
            roles_count[role] = []
        roles_count[role].append(user.username)
    
    for role, usernames in roles_count.items():
        print(f"   🔹 {role}: {', '.join(usernames)}")
    
    # 5. Vérification de la configuration
    print(f"\n{'='*60}")
    print("⚙️  CONFIGURATION DU SYSTÈME:")
    print(f"   🗄️  Base de données: {os.environ.get('USE_POSTGRESQL', 'False') == 'True' and 'PostgreSQL' or 'SQLite'}")
    print(f"   🐳 Django version: {django.get_version()}")
    print(f"   🔧 Debug mode: {os.environ.get('DEBUG', 'True') == 'True' and 'ON' or 'OFF'}")
    
    # 6. Vérification des middleware actifs
    print(f"\n🔒 MIDDLEWARE ACTIFS:")
    from django.conf import settings
    for middleware in settings.MIDDLEWARE:
        if 'permission' in middleware.lower() or 'auth' in middleware.lower():
            print(f"   🔐 {middleware}")
    
    print(f"\n{'='*80}")
    print("✅ VÉRIFICATION TERMINÉE")
    print("="*80)

def check_template_permissions():
    """Vérification des permissions dans les templates"""
    print("\n🎨 VÉRIFICATION DES TEMPLATES:")
    
    template_dir = "templates"
    if os.path.exists(template_dir):
        print(f"   📁 Templates trouvés dans: {template_dir}")
        
        # Vérifier les fichiers de base
        base_templates = [f for f in os.listdir(template_dir) if f.startswith('base')]
        print(f"   📄 Fichiers de base: {', '.join(base_templates)}")
        
        # Vérifier le template actuel
        current_template = "base_final_permissions.html"
        if os.path.exists(os.path.join(template_dir, current_template)):
            print(f"   ✅ Template actuel trouvé: {current_template}")
        else:
            print(f"   ❌ Template actuel non trouvé: {current_template}")
    else:
        print("   ❌ Dossier templates non trouvé")

if __name__ == "__main__":
    try:
        check_users_and_rights()
        check_template_permissions()
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        print("\n💡 DÉPANNAGE:")
        print("1. Vérifiez que Django est installé: pip install django")
        print("2. Vérifiez que vous êtes dans le bon dossier")
        print("3. Vérifiez que la base de données est accessible")
        print("4. Essayez: python manage.py migrate")
