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
            print("POST data reçu:", dict(request.POST))
            
            # Récupérer les paramètres
            type_etat = request.POST.get('type_etat')
            print(f"Type état: {type_etat}")
            
            if not type_etat:
                return JsonResponse({'success': False, 'error': 'Type d\'état manquant'})
            
            # Appliquer les mêmes filtres que la vue PDF (cohérence preview / génération)
            if type_etat == 'DEPENSE_FEUILLE':
                # LOGIQUE SIMPLE DIRECTE - sans fonction externe
                queryset = DepenseFeuille.objects.all()
                print(f"Total initial DepenseFeuille: {queryset.count()}")
                
                # Récupérer les filtres
                mois = request.POST.get('mois_depenses')  # Changé : get() au lieu de getlist()
                annee = request.POST.get('annee_depenses')
                natures = request.POST.get('natures_depenses')
                services = request.POST.get('services_depenses')
                banques = request.POST.get('banques_depenses')
                montant_min = request.POST.get('montant_min_depenses')
                montant_max = request.POST.get('montant_max_depenses')
                observation = request.POST.get('observation_depenses')
                
                print(f"Filtres reçus - Mois: {mois}, Année: {annee}, Nature: {natures}, Service: {services}, Banque: {banques}")
                
                # Appliquer les filtres
                if mois and mois.isdigit() and mois != '':
                    queryset = queryset.filter(mois=int(mois))
                    print(f"✅ Filtré par mois: {mois} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucun mois sélectionné ou 'Toutes'")
                
                if annee and annee.isdigit() and annee != '':
                    queryset = queryset.filter(annee=int(annee))
                    print(f"✅ Filtré par annee: {annee} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucune année sélectionnée ou 'Toutes'")
                
                # Logique simple pour les ChoiceField
                if natures and natures.isdigit() and natures != '':
                    queryset = queryset.filter(nature_economique_id=int(natures))
                    print(f"✅ Filtré par nature: {natures} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucune nature sélectionnée ou 'Toutes'")
                
                if services and services.isdigit() and services != '':
                    queryset = queryset.filter(service_beneficiaire_id=int(services))
                    print(f"✅ Filtré par service: {services} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucun service sélectionné ou 'Toutes'")
                
                if banques and banques.isdigit() and banques != '':
                    queryset = queryset.filter(banque_id=int(banques))
                    print(f"✅ Filtré par banque: {banques} -> {queryset.count()} résultats")
                else:
                    print(f"ℹ️ Aucune banque sélectionnée ou 'Toutes'")
                
                if montant_min and str(montant_min).replace('.', '').replace('-', '').isdigit():
                    queryset = queryset.filter(montant_fc__gte=Decimal(str(montant_min)))
                    print(f"✅ Filtré par montant_min: {montant_min} -> {queryset.count()} résultats")
                
                if montant_max and str(montant_max).replace('.', '').replace('-', '').isdigit():
                    queryset = queryset.filter(montant_fc__lte=Decimal(str(montant_max)))
                    print(f"✅ Filtré par montant_max: {montant_max} -> {queryset.count()} résultats")
                
                if observation and observation.strip():
                    queryset = queryset.filter(observation__icontains=observation.strip())
                    print(f"✅ Filtré par observation: {observation} -> {queryset.count()} résultats")
                
                # Limiter pour le preview
                queryset = queryset.order_by('-date')[:50]
                print(f"📊 Résultat final: {queryset.count()} lignes")
                
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
                
                print(f"📊 Détails: {len(lignes)} lignes traitées, Total CDF: {total_cdf}, Total USD: {total_usd}")
                
            elif type_etat == 'RECETTE_FEUILLE':
                from tableau_bord_feuilles.views_rapports import _queryset_recettes_filtre
                queryset = _queryset_recettes_filtre(request)
                print(f"Total recettes filtrées: {queryset.count()}")
                queryset = queryset.order_by('-date')[:50]
                
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
                
                print(f"📊 Résultat recettes: {len(lignes)} lignes, Total CDF: {total_cdf}, Total USD: {total_usd}")
            else:
                return JsonResponse({'success': False, 'error': 'Type d\'état non valide'})
            
            print(f"Résultat FINAL: {len(lignes)} lignes, Total CDF: {total_cdf}, Total USD: {total_usd}")
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
