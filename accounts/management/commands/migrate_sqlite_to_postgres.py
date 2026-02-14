"""
Commande pour migrer toutes les données de SQLite vers PostgreSQL.

Usage:
    python manage.py migrate_sqlite_to_postgres
    python manage.py migrate_sqlite_to_postgres --sqlite-path db.sqlite3
"""
import os
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Migre toutes les données de la base SQLite vers PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sqlite-path',
            type=str,
            default=None,
            help='Chemin vers le fichier SQLite (défaut: db.sqlite3 à la racine du projet)',
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Ne pas demander de confirmation',
        )

    def handle(self, *args, **options):
        sqlite_path = options.get('sqlite_path')
        base_dir = Path(settings.BASE_DIR)

        if sqlite_path is None:
            sqlite_path = base_dir / 'db.sqlite3'

        sqlite_path = Path(sqlite_path).resolve()

        if not sqlite_path.exists():
            self.stderr.write(self.style.ERROR(f'Fichier SQLite introuvable: {sqlite_path}'))
            return

        # Vérifier que la base par défaut est PostgreSQL
        default_engine = settings.DATABASES['default']['ENGINE']
        if 'postgresql' not in default_engine:
            self.stderr.write(self.style.ERROR(
                'La base par défaut doit être PostgreSQL. '
                'Configurez USE_POSTGRESQL=True dans settings.'
            ))
            return

        if not options.get('no_input'):
            self.stdout.write(self.style.WARNING(
                f'Migration SQLite -> PostgreSQL\n'
                f'  Source: {sqlite_path}\n'
                f'  Cible:  PostgreSQL (default)\n'
                f'Les données existantes dans PostgreSQL peuvent être modifiées.'
            ))
            confirm = input('Continuer ? [y/N]: ')
            if confirm.lower() not in ('y', 'yes', 'o', 'oui'):
                self.stdout.write('Migration annulée.')
                return

        self.stdout.write('Début de la migration...')

        # Ajouter la base SQLite comme source temporaire
        settings.DATABASES['sqlite_source'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(sqlite_path),
        }

        try:
            # Créer un fichier temporaire pour le dump
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False,
                dir=base_dir,
            ) as f:
                dump_file = f.name

            try:
                # 1. Exporter les données depuis SQLite
                self.stdout.write('Export des données depuis SQLite...')
                call_command(
                    'dumpdata',
                    database='sqlite_source',
                    natural_foreign=True,
                    indent=2,
                    exclude=['contenttypes', 'auth.Permission', 'sessions.Session', 'admin.LogEntry'],
                    output=dump_file,
                )

                # 2. Importer dans PostgreSQL (default = PostgreSQL)
                self.stdout.write('Import des données vers PostgreSQL...')
                call_command('loaddata', dump_file, verbosity=1, ignorenonexistent=True)

                self.stdout.write(self.style.SUCCESS('\n✓ Migration terminée avec succès!'))

            finally:
                # Supprimer le fichier temporaire
                if os.path.exists(dump_file):
                    os.unlink(dump_file)

        finally:
            # Retirer la config SQLite temporaire
            if 'sqlite_source' in settings.DATABASES:
                del settings.DATABASES['sqlite_source']
