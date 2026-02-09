from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('demandes', '0009_depensefeuille_banque_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='depensefeuille',
            name='service_beneficiaire',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='depense_feuilles',
                to='accounts.service',
                verbose_name='Service bénéficiaire',
            ),
        ),
    ]
