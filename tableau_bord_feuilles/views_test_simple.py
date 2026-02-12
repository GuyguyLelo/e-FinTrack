from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse
from demandes.models import DepenseFeuille
from recettes.models import RecetteFeuille

class TestSimpleView(LoginRequiredMixin, View):
    """Vue de test ultra-simple"""
    
    def get(self, request, *args, **kwargs):
        return render(request, 'tableau_bord_feuilles/test_simple.html')
    
    def post(self, request, *args, **kwargs):
        try:
            type_etat = request.POST.get('type_etat')
            print(f"TEST SIMPLE - Type état: {type_etat}")
            
            if type_etat == 'DEPENSE_FEUILLE':
                # Test ultra-simple
                depenses = DepenseFeuille.objects.all()[:5]
                lignes = []
                for dep in depenses:
                    lignes.append({
                        'date': dep.date.strftime('%d/%m/%Y'),
                        'libelle_depenses': dep.libelle_depenses[:50],
                        'montant_fc': float(dep.montant_fc),
                    })
                
                print(f"TEST SIMPLE - {len(lignes)} dépenses trouvées")
                return JsonResponse({
                    'success': True,
                    'lignes': lignes,
                    'count': len(lignes),
                    'message': f'Test simple - {len(lignes)} dépenses'
                })
                
            elif type_etat == 'RECETTE_FEUILLE':
                # Test ultra-simple
                recettes = RecetteFeuille.objects.all()[:5]
                lignes = []
                for rec in recettes:
                    lignes.append({
                        'date': rec.date.strftime('%d/%m/%Y'),
                        'libelle_recette': rec.libelle_recette[:50],
                        'montant_fc': float(rec.montant_fc),
                    })
                
                print(f"TEST SIMPLE - {len(lignes)} recettes trouvées")
                return JsonResponse({
                    'success': True,
                    'lignes': lignes,
                    'count': len(lignes),
                    'message': f'Test simple - {len(lignes)} recettes'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Type invalide'})
                
        except Exception as e:
            print(f"TEST SIMPLE - ERREUR: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
