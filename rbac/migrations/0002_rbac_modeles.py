"""
Migration manuelle pour le système RBAC basé sur les modèles
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='permissionmodele',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100, verbose_name='Nom de la permission')),
                ('description', models.TextField(verbose_name='Description')),
                ('modele_django', models.CharField(max_length=100, verbose_name='Modèle Django')),
                ('app_label', models.CharField(max_length=50, verbose_name='Application Django')),
                ('action', models.CharField(max_length=20, verbose_name='Action', choices=[
                    ('liste', 'Voir la liste'),
                    ('creer', 'Créer'),
                    ('modifier', 'Modifier'),
                    ('supprimer', 'Supprimer'),
                    ('valider', 'Valider'),
                    ('exporter', 'Exporter'),
                    ('importer', 'Importer'),
                ])),
                ('code', models.CharField(max_length=50, unique=True, verbose_name='Code technique')),
                ('url_pattern', models.CharField(max_length=200, blank=True, verbose_name='Pattern URL')),
                ('est_active', models.BooleanField(default=True, verbose_name='Permission active')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date création')),
            ],
            options={
                'verbose_name': 'Permission de modèle',
                'verbose_name_plural': 'Permissions de modèles',
                'ordering': ['modele_django', 'action'],
                'db_table': 'rbac_permissionmodele',
                'db_tablespace': '',
                'indexes': [],
            },
        ),
        migrations.CreateModel(
            name='rolemodele',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, unique=True, verbose_name='Nom du rôle')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='Code du rôle')),
                ('description', models.TextField(verbose_name='Description du rôle')),
                ('couleur', models.CharField(max_length=7, default='#007bff', verbose_name='Couleur')),
                ('icone', models.CharField(max_length=50, default='bi-person', verbose_name='Icône')),
                ('est_actif', models.BooleanField(default=True, verbose_name='Rôle actif')),
                ('est_systeme', models.BooleanField(default=False, verbose_name='Rôle système')),
                ('niveau_acces', models.IntegerField(default=1, verbose_name='Niveau d\'accès')),
                ('date_creation', models.DateTimeField(auto_now_add=True, verbose_name='Date création')),
            ],
            options={
                'verbose_name': 'Rôle (basé sur modèles)',
                'verbose_name_plural': 'Rôles (basés sur modèles)',
                'ordering': ['niveau_acces', 'nom'],
                'db_table': 'rbac_rolemodele',
                'db_tablespace': '',
                'indexes': [],
            },
        ),
        migrations.AddField(
            model_name='rolemodele',
            name='permissions_modeles',
            field=models.ManyToManyField(
                to='rbac.permissionmodele',
                related_name='roles',
                verbose_name='Permissions des modèles',
            ),
        ),
    ]
