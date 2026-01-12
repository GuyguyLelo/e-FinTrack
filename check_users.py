#!/usr/bin/env python
"""Script pour vérifier les utilisateurs créés"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
django.setup()

from accounts.models import User
from django.db.models import Count

print("=" * 60)
print("LISTE DES UTILISATEURS PAR RÔLE")
print("=" * 60)
print()

total = User.objects.count()
print(f"Total utilisateurs: {total}\n")

roles_count = User.objects.values('role').annotate(count=Count('role')).order_by('role')
print("Répartition par rôle:")
for r in roles_count:
    role_name = dict(User.ROLE_CHOICES).get(r['role'], r['role'])
    print(f"  - {role_name}: {r['count']} utilisateur(s)")

print("\n" + "=" * 60)
print("DÉTAILS DES UTILISATEURS")
print("=" * 60)
print()

for user in User.objects.all().order_by('role', 'username'):
    service_name = user.service.nom_service if user.service else 'N/A'
    print(f"Username: {user.username:20} | Rôle: {user.get_role_display():25} | Service: {service_name}")
print()

