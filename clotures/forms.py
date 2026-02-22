from django import forms
from .models import ClotureMensuelle


class ClotureMensuelleForm(forms.ModelForm):
    class Meta:
        model = ClotureMensuelle
        fields = ['observations']
        widgets = {
            'observations': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Ajoutez des observations sur cette clôture...'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['observations'].required = False
