# Custom migration: replace banque CharField by FK to Banque, preserve data

from django.db import migrations, models
import django.db.models.deletion


def populate_banque_fk(apps, schema_editor):
    """Remplit la FK banque à partir du nom (banque_old) en faisant correspondre Banque.nom_banque."""
    DepenseFeuille = apps.get_model('demandes', 'DepenseFeuille')
    Banque = apps.get_model('banques', 'Banque')
    for dep in DepenseFeuille.objects.all():
        if not dep.banque_old or not dep.banque_old.strip():
            continue
        nom = dep.banque_old.strip()
        banque = Banque.objects.filter(nom_banque__iexact=nom).first()
        if not banque:
            banque = Banque.objects.filter(nom_banque__icontains=nom).first()
        if banque:
            dep.banque = banque
            dep.save(update_fields=['banque_id'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('banques', '0002_comptebancaire_date_solde_courant'),
        ('demandes', '0008_depensefeuille_nature_fk'),
    ]

    operations = [
        migrations.RenameField(
            model_name='depensefeuille',
            old_name='banque',
            new_name='banque_old',
        ),
        migrations.AddField(
            model_name='depensefeuille',
            name='banque',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='depense_feuilles',
                to='banques.banque',
                verbose_name='Banque',
            ),
        ),
        migrations.RunPython(populate_banque_fk, noop),
        migrations.RemoveField(
            model_name='depensefeuille',
            name='banque_old',
        ),
    ]
