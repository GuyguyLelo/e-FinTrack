"""
Script pour importer toutes les données de dépenses
Ce script lit les données depuis stdin ou un fichier et les importe
"""
import sys
import subprocess

def main():
    if len(sys.argv) > 1:
        # Lire depuis un fichier
        filename = sys.argv[1]
        with open(filename, 'r', encoding='utf-8') as f:
            data = f.read()
    else:
        # Lire depuis stdin
        data = sys.stdin.read()
    
    # Utiliser la commande de management Django
    from django.core.management import call_command
    from io import StringIO
    
    # Créer un StringIO pour capturer la sortie
    out = StringIO()
    
    # Appeler la commande
    call_command('import_depenses', data=data, user='admin', service='Direction Générale', statut='PAYEE', stdout=out)
    
    # Afficher la sortie
    print(out.getvalue())

if __name__ == '__main__':
    import os
    import django
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')
    django.setup()
    
    main()

