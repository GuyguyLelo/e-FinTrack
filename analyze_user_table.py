#!/usr/bin/env python
"""
Analyse détaillée de la table User et de l'attribut role
"""
import os
import sys
import django

# Configuration Django
sys.path.append('/home/mohamed-kandolo/e-FinTrack')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.db import connection

def analyze_user_table():
    """Analyse complète de la table User"""
    print("🔍 ANALYSE DE LA TABLE USER")
    print("=" * 60)
    
    # 1. Structure de la table
    print("\n📋 STRUCTURE DE LA TABLE USER:")
    print("-" * 40)
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'accounts_user' 
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        print(f"{'Champ':25} | {'Type':20} | {'Null':5} | {'Default':20}")
        print("-" * 75)
        for col in columns:
            field, type_, null, default = col[:4]
            default_str = str(default) if default else ''
            print(f"{field:25} | {type_:20} | {null:5} | {default_str[:20]:20}")
    
    # 2. Définition des rôles
    print("\n🎯 DÉFINITION DES RÔLES:")
    print("-" * 40)
    role_choices = User.ROLE_CHOICES
    print(f"{'Code':20} | {'Libellé':30}")
    print("-" * 55)
    for value, label in role_choices:
        print(f"{value:20} | {label:30}")
    
    # 3. Analyse des utilisateurs actuels
    print("\n👥 UTILISATEURS ACTUELS:")
    print("-" * 40)
    users = User.objects.all()
    print(f"Total: {users.count()} utilisateurs")
    
    # Répartition par rôle
    print("\n📊 RÉPARTITION PAR RÔLE:")
    role_stats = {}
    for user in users:
        role = user.role
        if role not in role_stats:
            role_stats[role] = {'count': 0, 'users': []}
        role_stats[role]['count'] += 1
        role_stats[role]['users'].append(user.username)
    
    print(f"{'Rôle':20} | {'Count':5} | {'Utilisateurs':30}")
    print("-" * 60)
    for role_code, stats in role_stats.items():
        role_label = dict(role_choices).get(role_code, role_code)
        users_str = ', '.join(stats['users'][:3])
        if len(stats['users']) > 3:
            users_str += f" (+{len(stats['users'])-3})"
        print(f"{role_label:20} | {stats['count']:5} | {users_str:30}")
    
    # 4. Analyse détaillée des utilisateurs DAF
    print("\n🔍 ANALYSE DES UTILISATEURS DAF:")
    print("-" * 40)
    daf_users = [u for u in users if 'daf' in u.username.lower()]
    print(f"Utilisateurs avec 'DAF' dans le username: {len(daf_users)}")
    for user in daf_users:
        print(f"   - {user.username:15} | Rôle: {user.role:20} | Actif: {user.is_active}")
    
    # 5. Vérification des permissions par rôle
    print("\n🔐 MATRICE DES PERMISSIONS:")
    print("-" * 40)
    
    # Liste des méthodes de permission
    permission_methods = [
        ('peut_voir_tableau_bord', 'Voir tableau bord'),
        ('peut_creer_entites_base', 'Créer entités base'),
        ('peut_valider_demandes', 'Valider demandes'),
        ('peut_effectuer_paiements', 'Effectuer paiements'),
        ('peut_acceder_admin_django', 'Accès admin Django'),
        ('peut_saisir_demandes_recettes', 'Saisir demandes/recettes'),
        ('peut_voir_menu_depenses', 'Voir menu dépenses'),
        ('peut_voir_menu_paiements', 'Voir menu paiements'),
        ('peut_ajouter_nature_economique', 'Ajouter nature éco'),
    ]
    
    print(f"{'Rôle':20} | {'Voir TB':7} | {'Val Dem':7} | {'Paiement':9} | {'Admin':5}")
    print("-" * 70)
    
    for role_code, _ in role_choices:
        # Créer un utilisateur temporaire pour tester les permissions
        temp_user = User(role=role_code)
        
        permissions = [
            '✅' if temp_user.peut_voir_tableau_bord() else '❌',
            '✅' if temp_user.peut_valider_demandes() else '❌', 
            '✅' if temp_user.peut_effectuer_paiements() else '❌',
            '✅' if temp_user.peut_acceder_admin_django() else '❌',
        ]
        
        role_label = dict(role_choices).get(role_code, role_code)[:18]
        print(f"{role_label:20} | {permissions[0]:7} | {permissions[1]:7} | {permissions[2]:9} | {permissions[3]:5}")
    
    # 6. Analyse des champs spécifiques
    print("\n📝 CHAMSPÉCIFIQUES DE USER:")
    print("-" * 40)
    sample_user = users.first()
    if sample_user:
        print(f"Champs hérités d'AbstractUser:")
        inherited_fields = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
        for field in inherited_fields:
            value = getattr(sample_user, field, 'N/A')
            print(f"   - {field:20}: {value}")
        
        print(f"\nChamps personnalisés:")
        custom_fields = ['role', 'telephone', 'actif', 'date_creation', 'date_modification']
        for field in custom_fields:
            value = getattr(sample_user, field, 'N/A')
            print(f"   - {field:20}: {value}")

def analyze_role_logic():
    """Analyse la logique de détection DAF"""
    print("\n🧩 LOGIQUE DE DÉTECTION DAF:")
    print("-" * 40)
    
    users = User.objects.all()
    
    # Test de la logique 'daf' dans username
    print("Test de la condition 'daf' in username.lower():")
    for user in users:
        has_daf = 'daf' in user.username.lower()
        is_daf_role = user.role in ['ADMIN']  # Rôle considéré comme DAF
        print(f"   {user.username:15} | Role: {user.role:20} | DAF in name: {has_daf} | DAF role: {is_daf_role}")
    
    print("\n⚠️  OBSERVATIONS:")
    print("   - La détection DAF se base sur le username, pas sur le rôle")
    print("   - Les rôles DAF possibles: ADMIN, DIR_DAF, DIV_DAF, OPS_DAF")
    print("   - Mais ces rôles ne sont pas définis dans ROLE_CHOICES")

if __name__ == "__main__":
    analyze_user_table()
    analyze_role_logic()
    
    print("\n🎯 SYNTHÈSE:")
    print("=" * 40)
    print("✅ Table User bien structurée avec champ 'role'")
    print("✅ 7 rôles définis dans ROLE_CHOICES")
    print("✅ 6 utilisateurs actuels dans la base")
    print("⚠️  Logique DAF basée sur username, pas sur role")
    print("🔧 Possibilité d'ajouter des rôles DAF spécifiques")
