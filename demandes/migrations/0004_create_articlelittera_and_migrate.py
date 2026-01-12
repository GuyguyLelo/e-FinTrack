# Generated migration

from django.db import migrations, models
import django.db.models.deletion


def migrate_article_littera_data(apps, schema_editor):
    """Migre les données article_littera existantes vers le nouveau modèle"""
    ArticleLittera = apps.get_model('demandes', 'ArticleLittera')
    Depense = apps.get_model('demandes', 'Depense')
    
    # Récupérer tous les codes article_littera uniques existants
    depenses = Depense.objects.exclude(article_littera='').exclude(article_littera__isnull=True)
    codes_uniques = set()
    
    for depense in depenses:
        if depense.article_littera:
            codes_uniques.add(depense.article_littera.strip())
    
    # Créer les articles littéra pour chaque code unique
    code_to_article = {}
    for code in codes_uniques:
        if code:
            article, created = ArticleLittera.objects.get_or_create(
                code=code,
                defaults={
                    'libelle': f'Article {code}',
                    'description': f'Article littéra {code}',
                    'actif': True
                }
            )
            code_to_article[code] = article
    
    # Mettre à jour les dépenses avec les nouveaux articles littéra
    for depense in depenses:
        if depense.article_littera and depense.article_littera.strip() in code_to_article:
            depense.article_littera_new = code_to_article[depense.article_littera.strip()]
            depense.save(update_fields=['article_littera_new'])


def reverse_migrate(apps, schema_editor):
    """Migration inverse : convertir les ForeignKey en CharField"""
    Depense = apps.get_model('demandes', 'Depense')
    
    for depense in Depense.objects.exclude(article_littera__isnull=True):
        if depense.article_littera:
            depense.article_littera = depense.article_littera.code
            depense.save(update_fields=['article_littera'])


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0003_depense'),
    ]

    operations = [
        # Étape 1 : Créer le modèle ArticleLittera
        migrations.CreateModel(
            name='ArticleLittera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Code Article')),
                ('libelle', models.CharField(max_length=200, verbose_name='Libellé')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('actif', models.BooleanField(default=True, verbose_name='Actif')),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('date_modification', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Article Littéra',
                'verbose_name_plural': 'Articles Littéra',
                'ordering': ['code'],
            },
        ),
        migrations.AddIndex(
            model_name='articlelittera',
            index=models.Index(fields=['code'], name='demandes_ar_code_0c6723_idx'),
        ),
        # Étape 2 : Ajouter un nouveau champ temporaire pour la ForeignKey
        migrations.AddField(
            model_name='depense',
            name='article_littera_new',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='depenses_new', to='demandes.articlelittera', verbose_name='Article Littéra'),
        ),
        # Étape 3 : Migrer les données
        migrations.RunPython(migrate_article_littera_data, reverse_migrate),
        # Étape 4 : Supprimer l'ancien champ CharField
        migrations.RemoveField(
            model_name='depense',
            name='article_littera',
        ),
        # Étape 5 : Renommer le nouveau champ
        migrations.RenameField(
            model_name='depense',
            old_name='article_littera_new',
            new_name='article_littera',
        ),
    ]
