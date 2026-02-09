from django import forms


class RapportFeuilleSelectionForm(forms.Form):
    """Formulaire pour la sélection des rapports feuilles"""
    
    annee = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Année"
    )
    
    mois = forms.ChoiceField(
        choices=[
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Mois"
    )
    
    def __init__(self, *args, **kwargs):
        annees_disponibles = kwargs.pop('annees_disponibles', [])
        super().__init__(*args, **kwargs)
        
        # Mettre à jour les choix d'années
        self.fields['annee'].choices = [(str(annee), str(annee)) for annee in annees_disponibles]
