# Generated manually to remove unique constraint on periode field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0002_add_beneficiaire_to_paiement'),
    ]

    operations = [
        # Remove unique constraint on periode field
        migrations.AlterField(
            model_name='relevedepense',
            name='periode',
            field=models.DateField(help_text='Période concernée'),
        ),
    ]
