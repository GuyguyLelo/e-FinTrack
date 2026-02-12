from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
from datetime import datetime

from demandes.models import DepenseFeuille, NatureEconomique
from recettes.models import RecetteFeuille
from banques.models import Banque
from accounts.models import Service


@method_decorator(csrf_exempt, name='dispatch')
class EtatsFeuillesPreviewView(LoginRequiredMixin, View):
    """Vue pour le preview des états feuilles"""
    
    def post(self, request, *args, **kwargs):
        try:
            print("=== DÉBUT DE LA REQUÊTE ===")
            print("POST data reçu:", request.POST)
            
            # Récupérer les paramètres
            type_etat = request.POST.get('type_etat')
            print(f"Type état: {type_etat}")
            
            if not type_etat:
                return JsonResponse({'success': False, 'error': 'Type d\'état manquant'})
            
            # LOGIQUE AVEC FILTRES SIMPLES : appliquer les filtres de base
            if type_etat == 'DEPENSE_FEUILLE':
                print("Application des filtres pour dépenses")
                queryset = DepenseFeuille.objects.all()
                
                # Récupérer les filtres de base
                mois = request.POST.getlist('mois_depenses')
                annee = request.POST.get('annee_depenses')
                
                print(f"Filtres - Mois: {mois}, Année: {annee}")
                
                # Appliquer les filtres de base
                if mois:
                    mois_list = [int(m) for m in mois if m.isdigit()]
                    if mois_list:
                        queryset = queryset.filter(mois__in=mois_list)
                        print(f"✅ Filtré par mois: {mois_list}")
                
                if annee and annee.isdigit():
                    queryset = queryset.filter(annee=int(annee))
                    print(f"✅ Filtré par annee: {annee}")
                
                # Trier par date et limiter à 20 résultats
                queryset = queryset.order_by('-date')[:20]
                
                lignes = []
                total_cdf = Decimal('0.00')
                total_usd = Decimal('0.00')
                
                for dep in queryset:
                    lignes.append({
                        'date': dep.date.strftime('%d/%m/%Y'),
                        'libelle_depenses': dep.libelle_depenses[:100],
                        'nature_economique': dep.nature_economique.titre if dep.nature_economique else '',
                        'service_beneficiaire': dep.service_beneficiaire.nom_service if dep.service_beneficiaire else '',
                        'banque': dep.banque.nom_banque if dep.banque else '',
                        'montant_fc': float(dep.montant_fc),
                        'montant_usd': float(dep.montant_usd),
                        'observation': dep.observation[:100] if dep.observation else '',
                    })
                    total_cdf += dep.montant_fc
                    total_usd += dep.montant_usd
                
                print(f"📊 Résultat: {len(lignes)} lignes, Total CDF: {total_cdf}, Total USD: {total_usd}")
                
            elif type_etat == 'RECETTE_FEUILLE':
                print("Application des filtres pour recettes")
                queryset = RecetteFeuille.objects.all()
                
                # Récupérer les filtres de base
                mois = request.POST.getlist('mois_recettes')
                annee = request.POST.get('annee_recettes')
                
                print(f"Filtres - Mois: {mois}, Année: {annee}")
                
                # Appliquer les filtres de base
                if mois:
                    mois_list = [int(m) for m in mois if m.isdigit()]
                    if mois_list:
                        queryset = queryset.filter(mois__in=mois_list)
                        print(f"✅ Filtré par mois: {mois_list}")
                
                if annee and annee.isdigit():
                    queryset = queryset.filter(annee=int(annee))
                    print(f"✅ Filtré par annee: {annee}")
                
                # Trier par date et limiter à 20 résultats
                queryset = queryset.order_by('-date')[:20]
                
                lignes = []
                total_cdf = Decimal('0.00')
                total_usd = Decimal('0.00')
                
                for rec in queryset:
                    lignes.append({
                        'date': rec.date.strftime('%d/%m/%Y'),
                        'libelle_recette': rec.libelle_recette[:100],
                        'banque': rec.banque.nom_banque if rec.banque else '',
                        'montant_fc': float(rec.montant_fc),
                        'montant_usd': float(rec.montant_usd),
                    })
                    total_cdf += rec.montant_fc
                    total_usd += rec.montant_usd
                
                print(f"📊 Résultat: {len(lignes)} lignes, Total CDF: {total_cdf}, Total USD: {total_usd}")
            else:
                return JsonResponse({'success': False, 'error': 'Type d\'état non valide'})
            
            print(f"Résultat TEST: {len(lignes)} lignes, Total CDF: {total_cdf}, Total USD: {total_usd}")
            print("=== FIN DE LA REQUÊTE ===")
            
            return JsonResponse({
                'success': True,
                'lignes': lignes,
                'count': len(lignes),
                'total_cdf': float(total_cdf),
                'total_usd': float(total_usd),
            })
            
        except Exception as e:
            print(f"ERREUR CAPTURÉE: {str(e)}")
            import traceback
            print("TRACEBACK COMPLET:")
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': f'Erreur: {str(e)}'})


@method_decorator(csrf_exempt, name='dispatch')
class EtatsFeuillesGenererView(LoginRequiredMixin, View):
    """Vue pour générer les états feuilles"""
    
    def post(self, request, *args, **kwargs):
        try:
            # Pour l'instant, rediriger vers les vues PDF existantes
            format_sortie = request.POST.get('format_sortie', 'PDF')
            type_etat = request.POST.get('type_etat')
            
            if format_sortie == 'PDF':
                if type_etat == 'RECETTE_FEUILLE':
                    # Rediriger vers la vue PDF des recettes
                    return JsonResponse({'success': True, 'etat_id': 'recette_pdf'})
                elif type_etat == 'DEPENSE_FEUILLE':
                    # Rediriger vers la vue PDF des dépenses
                    return JsonResponse({'success': True, 'etat_id': 'depense_pdf'})
                else:
                    # Rediriger vers le tableau général PDF
                    return JsonResponse({'success': True, 'etat_id': 'tableau_general_pdf'})
            else:
                # Pour Excel, pour l'instant retourner une erreur
                return JsonResponse({'success': False, 'error': 'Export Excel non encore implémenté'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
