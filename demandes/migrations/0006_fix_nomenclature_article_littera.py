# Generated migration

from django.db import migrations, models
import django.db.models.deletion
from datetime import datetime


def add_article_littera_to_nomenclature(apps, schema_editor):
    """Ajoute le champ article_littera manquant aux nomenclatures existantes"""
    ArticleLittera = apps.get_model('demandes', 'ArticleLittera')
    NomenclatureDepense = apps.get_model('demandes', 'NomenclatureDepense')
    
    # Pour chaque nomenclature existante, créer un article littéra par défaut si nécessaire
    for nomencl in NomenclatureDepense.objects.all():
        if not hasattr(nomencl, 'article_littera_id') or not nomencl.article_littera_id:
            # Créer un article littéra par défaut
            article, _ = ArticleLittera.objects.get_or_create(
                code=f'DEFAULT-{nomencl.id}',
                defaults={
                    'libelle': f'Article par défaut {nomencl.id}',
                    'description': 'Article créé automatiquement',
                    'actif': True
                }
            )
            nomencl.article_littera_id = article.id
            nomencl.save(update_fields=['article_littera_id'])


def reverse_migrate(apps, schema_editor):
    """Migration inverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0005_add_annee_to_nomenclature_and_link_article_littera'),
    ]

    operations = [
        # Ajouter le champ article_littera s'il n'existe pas
        migrations.RunSQL(
            """
            -- Vérifier si la colonne existe, sinon l'ajouter
            SELECT CASE 
                WHEN COUNT(*) = 0 THEN 
                    'ALTER TABLE demandes_nomenclaturedepense ADD COLUMN article_littera_id INTEGER REFERENCES demandes_articlelittera(id);'
                ELSE 
                    'SELECT 1;'
            END
            FROM pragma_table_info('demandes_nomenclaturedepense') 
            WHERE name = 'article_littera_id';
            """,
            reverse_sql="-- Cannot reverse",
        ),
        # Ajouter la colonne directement
        migrations.AddField(
            model_name='nomenclaturedepense',
            name='article_littera',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='nomenclatures',
                to='demandes.articlelittera',
                verbose_name='Article Littéra'
            ),
        ),
        # Migrer les données
        migrations.RunPython(add_article_littera_to_nomenclature, reverse_migrate),
        # Rendre le champ obligatoire
        migrations.AlterField(
            model_name='nomenclaturedepense',
            name='article_littera',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='nomenclatures',
                to='demandes.articlelittera',
                verbose_name='Article Littéra'
            ),
        ),
    ]
