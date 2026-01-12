# Generated migration

from django.db import migrations, models
import django.db.models.deletion
from datetime import datetime


def migrate_nomenclature_data(apps, schema_editor):
    """Migre les données de nomenclature vers le nouveau modèle avec année et ForeignKey"""
    ArticleLittera = apps.get_model('demandes', 'ArticleLittera')
    NomenclatureDepense = apps.get_model('demandes', 'NomenclatureDepense')
    current_year = datetime.now().year
    
    # Pour chaque nomenclature existante
    for nomencl in NomenclatureDepense.objects.all():
        # Trouver ou créer l'article littéra correspondant
        article_code = nomencl.article_littera.strip() if nomencl.article_littera else None
        
        if article_code:
            article, created = ArticleLittera.objects.get_or_create(
                code=article_code,
                defaults={
                    'libelle': nomencl.libelle_article[:200] if nomencl.libelle_article else f'Article {article_code}',
                    'description': f'Nomenclature {article_code}',
                    'actif': nomencl.actif
                }
            )
            
            # Mettre à jour la nomenclature avec l'article littéra et l'année
            nomencl.article_littera_id = article.id
            nomencl.annee = current_year
            nomencl.save(update_fields=['article_littera_id', 'annee'])


def reverse_migrate(apps, schema_editor):
    """Migration inverse"""
    NomenclatureDepense = apps.get_model('demandes', 'NomenclatureDepense')
    
    for nomencl in NomenclatureDepense.objects.all():
        if nomencl.article_littera:
            nomencl.article_littera = nomencl.article_littera.code
            nomencl.save(update_fields=['article_littera'])


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0004_create_articlelittera_and_migrate'),
    ]

    operations = [
        # Étape 1 : Ajouter le champ annee avec valeur par défaut
        migrations.AddField(
            model_name='nomenclaturedepense',
            name='annee',
            field=models.IntegerField(default=2025, verbose_name="Année", help_text="Année d'application de cette nomenclature"),
            preserve_default=False,
        ),
        # Étape 2 : Ajouter un nouveau champ temporaire pour la ForeignKey
        migrations.AddField(
            model_name='nomenclaturedepense',
            name='article_littera_new',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='nomenclatures_new',
                to='demandes.articlelittera',
                verbose_name='Article Littéra'
            ),
        ),
        # Étape 3 : Migrer les données
        migrations.RunPython(migrate_nomenclature_data, reverse_migrate),
        # Étape 4 : Supprimer l'ancien champ CharField
        migrations.RemoveField(
            model_name='nomenclaturedepense',
            name='article_littera',
        ),
        # Étape 5 : Renommer le nouveau champ
        migrations.RenameField(
            model_name='nomenclaturedepense',
            old_name='article_littera_new',
            new_name='article_littera',
        ),
        # Étape 6 : Rendre le champ article_littera obligatoire
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
        # Étape 7 : Ajouter la contrainte unique_together
        migrations.AlterUniqueTogether(
            name='nomenclaturedepense',
            unique_together={('article_littera', 'annee')},
        ),
        # Étape 8 : Ajouter les index
        migrations.AddIndex(
            model_name='nomenclaturedepense',
            index=models.Index(fields=['annee'], name='demandes_no_annee_idx'),
        ),
        migrations.AddIndex(
            model_name='nomenclaturedepense',
            index=models.Index(fields=['article_littera', 'annee'], name='demandes_no_art_annee_idx'),
        ),
    ]
