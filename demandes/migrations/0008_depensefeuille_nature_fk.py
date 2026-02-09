# Custom migration: replace article_littera by ForeignKey to NatureEconomique

from django.db import migrations, models
import django.db.models.deletion


def populate_nature_fk(apps, schema_editor):
    """Remplit nature_economique à partir de article_littera_old (correspondance par code)."""
    DepenseFeuille = apps.get_model('demandes', 'DepenseFeuille')
    NatureEconomique = apps.get_model('demandes', 'NatureEconomique')
    for dep in DepenseFeuille.objects.all():
        if not getattr(dep, 'article_littera_old', None) or not str(dep.article_littera_old).strip():
            continue
        code = str(dep.article_littera_old).strip().replace(' ', '')
        nature = NatureEconomique.objects.filter(code=code).first()
        if not nature:
            nature = NatureEconomique.objects.filter(code__iexact=code).first()
        if nature:
            dep.nature_economique = nature
            dep.save(update_fields=['nature_economique_id'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0007_depense_feuille'),
    ]

    operations = [
        migrations.RenameField(
            model_name='depensefeuille',
            old_name='article_littera',
            new_name='article_littera_old',
        ),
        migrations.AddField(
            model_name='depensefeuille',
            name='nature_economique',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='depense_feuilles',
                to='demandes.natureeconomique',
                verbose_name='Nature économique',
            ),
        ),
        migrations.RunPython(populate_nature_fk, noop),
        migrations.RemoveField(
            model_name='depensefeuille',
            name='article_littera_old',
        ),
    ]
