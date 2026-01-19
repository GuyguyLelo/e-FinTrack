# Generated manually to fix missing beneficiaire column
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paiement',
            name='beneficiaire',
            field=models.CharField(default='', max_length=50, verbose_name='Beneficiaire'),
            preserve_default=False,
        ),
    ]
