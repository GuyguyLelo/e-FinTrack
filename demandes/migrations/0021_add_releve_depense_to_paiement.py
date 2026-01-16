# Generated migration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('demandes', '0020_paiement_and_more'),
    ]

    operations = [
        # Supprimer l'ancien champ releve_bancaire
        migrations.RemoveField(
            model_name='paiement',
            name='releve_bancaire',
        ),
        # Ajouter le nouveau champ releve_depense
        migrations.AddField(
            model_name='paiement',
            name='releve_depense',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='paiements',
                to='demandes.relevedepense',
                verbose_name='Relevé de dépenses'
            ),
        ),
    ]
