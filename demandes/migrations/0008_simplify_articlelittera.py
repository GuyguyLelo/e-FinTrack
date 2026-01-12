# Generated migration

from django.db import migrations, models


def migrate_data_to_designation(apps, schema_editor):
    """Migre les données libelle vers designation"""
    ArticleLittera = apps.get_model('demandes', 'ArticleLittera')
    
    for article in ArticleLittera.objects.all():
        # Si designation n'existe pas, utiliser libelle
        if not hasattr(article, 'designation') or not article.designation:
            article.designation = article.libelle if hasattr(article, 'libelle') else f'Article {article.code}'
            article.save(update_fields=['designation'])


def reverse_migrate(apps, schema_editor):
    """Migration inverse"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0007_alter_nomenclaturedepense_options_and_more'),
    ]

    operations = [
        # Étape 1 : Ajouter le champ designation
        migrations.AddField(
            model_name='articlelittera',
            name='designation',
            field=models.CharField(max_length=200, null=True, blank=True, verbose_name='Désignation'),
        ),
        # Étape 2 : Migrer les données
        migrations.RunPython(migrate_data_to_designation, reverse_migrate),
        # Étape 3 : Supprimer les champs inutiles
        migrations.RemoveField(
            model_name='articlelittera',
            name='libelle',
        ),
        migrations.RemoveField(
            model_name='articlelittera',
            name='description',
        ),
        migrations.RemoveField(
            model_name='articlelittera',
            name='actif',
        ),
        migrations.RemoveField(
            model_name='articlelittera',
            name='date_creation',
        ),
        migrations.RemoveField(
            model_name='articlelittera',
            name='date_modification',
        ),
        # Étape 4 : Rendre designation obligatoire
        migrations.AlterField(
            model_name='articlelittera',
            name='designation',
            field=models.CharField(max_length=200, verbose_name='Désignation'),
        ),
    ]
