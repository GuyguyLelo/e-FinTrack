# Generated migration

from django.db import migrations, models
import django.db.models.deletion
from datetime import date
from django.db.migrations.operations.fields import RemoveField


def migrate_nomenclature_relationship(apps, schema_editor):
    """Migre la relation de NomenclatureDepense.article_littera vers ArticleLittera.nomenclature"""
    ArticleLittera = apps.get_model('demandes', 'ArticleLittera')
    NomenclatureDepense = apps.get_model('demandes', 'NomenclatureDepense')
    
    # Pour chaque nomenclature qui a un article_littera
    for nomencl in NomenclatureDepense.objects.all():
        if hasattr(nomencl, 'article_littera_id') and nomencl.article_littera_id:
            # Mettre à jour l'article_littera pour qu'il pointe vers cette nomenclature
            ArticleLittera.objects.filter(id=nomencl.article_littera_id).update(nomenclature_id=nomencl.id)


def set_default_date_publication(apps, schema_editor):
    """Définit une date de publication par défaut pour les nomenclatures qui n'en ont pas"""
    NomenclatureDepense = apps.get_model('demandes', 'NomenclatureDepense')
    
    # Pour chaque nomenclature sans date_publication, utiliser le 1er janvier de l'année
    for nomencl in NomenclatureDepense.objects.filter(date_publication__isnull=True):
        nomencl.date_publication = date(nomencl.annee, 1, 1)
        nomencl.save(update_fields=['date_publication'])


def reverse_migrate(apps, schema_editor):
    """Migration inverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0008_simplify_articlelittera'),
    ]

    operations = [
        # Étape 1 : Définir une date_publication par défaut pour les nomenclatures existantes
        migrations.RunPython(set_default_date_publication, reverse_migrate),
        
        # Étape 2 : Rendre date_publication non-nullable
        migrations.AlterField(
            model_name='nomenclaturedepense',
            name='date_publication',
            field=models.DateField(help_text='Date de publication de cette nomenclature', verbose_name='Date de publication'),
        ),
        
        # Étape 3 : Ajouter le champ nomenclature à ArticleLittera (nullable d'abord)
        migrations.AddField(
            model_name='articlelittera',
            name='nomenclature',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='articles_littera',
                to='demandes.nomenclaturedepense',
                verbose_name='Nomenclature'
            ),
        ),
        
        # Étape 4 : Migrer les données de la relation inverse
        migrations.RunPython(migrate_nomenclature_relationship, reverse_migrate),
        
        # Étape 5 : Ajouter l'index sur nomenclature
        migrations.AddIndex(
            model_name='articlelittera',
            index=models.Index(fields=['nomenclature'], name='demandes_ar_nomencl_cb2fde_idx'),
        ),
        
        # Étape 6 : Supprimer le champ article_littera de NomenclatureDepense
        # Utiliser SeparateDatabaseAndState pour gérer l'état et la base de données séparément
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # Opération sur la base de données : supprimer la colonne si elle existe
                migrations.RunSQL(
                    """
                    -- Vérifier si la colonne existe avant de la supprimer
                    -- SQLite ne supporte pas DROP COLUMN directement
                    CREATE TABLE IF NOT EXISTS demandes_nomenclaturedepense_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        annee INTEGER NOT NULL,
                        date_publication DATE NOT NULL,
                        statut VARCHAR(10) NOT NULL DEFAULT 'EN_COURS'
                    );
                    INSERT INTO demandes_nomenclaturedepense_new (id, annee, date_publication, statut)
                    SELECT id, annee, date_publication, statut FROM demandes_nomenclaturedepense;
                    DROP TABLE demandes_nomenclaturedepense;
                    ALTER TABLE demandes_nomenclaturedepense_new RENAME TO demandes_nomenclaturedepense;
                    """,
                    reverse_sql="-- Cannot reverse",
                ),
            ],
            state_operations=[
                # Opération sur l'état : supprimer le champ du modèle
                migrations.RemoveField(
                    model_name='nomenclaturedepense',
                    name='article_littera',
                ),
            ],
        ),
    ]

