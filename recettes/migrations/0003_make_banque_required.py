# Generated migration for making banque field non-nullable

from django.db import migrations, models
import django.db.models.deletion


def set_default_banque(apps, schema_editor):
    """Set a default bank for all receipts without a bank"""
    Recette = apps.get_model('recettes', 'Recette')
    Banque = apps.get_model('banques', 'Banque')
    
    # Get the first bank
    default_bank = Banque.objects.first()
    if default_bank:
        Recette.objects.filter(banque__isnull=True).update(banque=default_bank)


class Migration(migrations.Migration):

    dependencies = [
        ('banques', '0001_initial'),
        ('recettes', '0002_alter_recette_banque_alter_recette_compte_bancaire'),
    ]

    operations = [
        # First, ensure all receipts have a bank
        migrations.RunPython(set_default_banque, migrations.RunPython.noop),
        
        # Then make the field non-nullable
        migrations.AlterField(
            model_name='recette',
            name='banque',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, 
                related_name='recettes', 
                to='banques.banque'
            ),
        ),
    ]
