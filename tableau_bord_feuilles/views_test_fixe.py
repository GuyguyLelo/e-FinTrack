from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse

class TestFixeView(LoginRequiredMixin, View):
    """Vue de test avec réponse fixe"""
    
    def get(self, request, *args, **kwargs):
        return render(request, 'tableau_bord_feuilles/test_fixe.html')
    
    def post(self, request, *args, **kwargs):
        try:
            type_etat = request.POST.get('type_etat')
            print(f"TEST FIXE - Type reçu: {type_etat}")
            
            # Réponse fixe pour tester
            if type_etat == 'DEPENSE_FEUILLE':
                return JsonResponse({
                    'success': True,
                    'lignes': [
                        {
                            'date': '07/05/2025',
                            'libelle_depenses': 'Test dépense 1',
                            'montant_fc': 100000.00,
                        },
                        {
                            'date': '07/05/2025',
                            'libelle_depenses': 'Test dépense 2',
                            'montant_fc': 200000.00,
                        }
                    ],
                    'count': 2,
                    'message': 'Test fixe - 2 dépenses (DONNÉES FIXES)'
                })
            elif type_etat == 'RECETTE_FEUILLE':
                return JsonResponse({
                    'success': True,
                    'lignes': [
                        {
                            'date': '05/05/2025',
                            'libelle_recette': 'Test recette 1',
                            'montant_fc': 500000.00,
                        },
                        {
                            'date': '05/05/2025',
                            'libelle_recette': 'Test recette 2',
                            'montant_fc': 750000.00,
                        }
                    ],
                    'count': 2,
                    'message': 'Test fixe - 2 recettes (DONNÉES FIXES)'
                })
            else:
                return JsonResponse({'success': False, 'error': 'Type invalide'})
                
        except Exception as e:
            print(f"TEST FIXE - ERREUR: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
