from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q, Count
from django.utils import timezone
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import html
from datetime import datetime

# Imports pour PDF
try:
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from io import BytesIO
    from urllib.parse import unquote
    REPORTLAB_AVAILABLE = True

    def _draw_footer(canvas, doc, page_count=None):
        """Pied de page : Page x de xx à gauche, date du jour à droite"""
        from datetime import date
        date_str = date.today().strftime('%d/%m/%Y')
        page_num = canvas.getPageNumber()
        total = page_count if page_count else page_num
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawString(50, 25, f"Page {page_num} de {total}")
        canvas.drawRightString(792, 25, date_str)
        canvas.restoreState()

    def _footer_on_first(canvas, doc):
        _draw_footer(canvas, doc)

    def _footer_on_later(canvas, doc):
        _draw_footer(canvas, doc)
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    print(f"WARNING: ReportLab n'est pas disponible: {e}. Les rapports PDF ne fonctionneront pas.")

from demandes.models import DepenseFeuille, NatureEconomique
from recettes.models import RecetteFeuille
from banques.models import Banque
from accounts.models import Service


@method_decorator(csrf_exempt, name='dispatch')
class EtatsFeuillesPreviewView(View):
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
            if type_etat in ['depense_par_nature', 'depense_par_mois', 'rapport_par_banque', 'synthese_par_banque', 'synthese_par_depenses']:
                # Utiliser la logique DEPENSE_FEUILLE pour les nouveaux états
                queryset = DepenseFeuille.objects.all()
                print(f"Total initial DepenseFeuille: {queryset.count()}")
                
                # Récupérer les filtres selon le type d'état
                if type_etat == 'depense_par_nature':
                    mois = request.POST.get('mois_nature')
                    annee = request.POST.get('annee_nature')
                    nature = request.POST.get('nature_economique')
                    print(f"Filtres dépense par nature - Mois: {mois}, Année: {annee}, Nature: {nature}")
                    
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    if nature and nature.isdigit() and nature != '':
                        queryset = queryset.filter(nature_economique_id=int(nature))
                        
                elif type_etat == 'depense_par_mois':
                    mois = request.POST.get('mois_depense')
                    annee = request.POST.get('annee_mois')
                    print(f"Filtres dépense par mois - Mois: {mois}, Année: {annee}")
                    
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                        
                elif type_etat == 'rapport_par_banque':
                    mois = request.POST.get('mois_banque')
                    annee = request.POST.get('annee_banque')
                    banque = request.POST.get('banque_rapport')
                    print(f"Filtres rapport par banque - Mois: {mois}, Année: {annee}, Banque: {banque}")
                    
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    if banque and banque.isdigit() and banque != '':
                        queryset = queryset.filter(banque_id=int(banque))
                        
                elif type_etat == 'synthese_par_banque':
                    mois = request.POST.get('mois_synthese_banque')
                    annee = request.POST.get('annee_synthese_banque')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    # Aperçu : regroupement par banque (une ligne par banque + total général)
                    groups = list(queryset.values('banque_id', 'banque__nom_banque').annotate(
                        total_cdf=Sum('montant_fc'), total_usd=Sum('montant_usd')
                    ).order_by('banque__nom_banque'))
                    total_general_fc = sum((g['total_cdf'] or Decimal('0')) for g in groups)
                    total_general_usd = sum((g['total_usd'] or Decimal('0')) for g in groups)
                    groupes_banque = [
                        {
                            'banque_nom': g.get('banque__nom_banque') or 'Sans banque',
                            'total_cdf': float(g['total_cdf'] or 0),
                            'total_usd': float(g['total_usd'] or 0),
                        }
                        for g in groups
                    ]
                    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                    if annee and str(annee).isdigit():
                        periode_label = f'{mois_noms[int(mois)]} {annee}' if (mois and str(mois).isdigit() and 1 <= int(mois) <= 12) else annee
                    else:
                        periode_label = 'Toutes périodes'
                    return JsonResponse({
                        'success': True,
                        'preview_synthese_banque': True,
                        'periode_label': periode_label,
                        'groupes_banque': groupes_banque,
                        'total_general_cdf': float(total_general_fc),
                        'total_general_usd': float(total_general_usd),
                    })
                        
                elif type_etat == 'synthese_par_depenses':
                    mois = request.POST.get('mois_synthese_depenses')
                    annee = request.POST.get('annee_synthese_depenses')
                    print(f"Filtres synthèse par dépenses - Mois: {mois}, Année: {annee}")
                    
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                
                # Préparer les données pour la réponse
                lignes = []
                total_cdf = Decimal('0.00')
                total_usd = Decimal('0.00')
                
                # Pagination
                page = int(request.POST.get('page', 1))
                page_size = 50
                start = (page - 1) * page_size
                end = start + page_size
                
                queryset_paginated = queryset.order_by('-date')[start:end]
                
                for dep in queryset_paginated:
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
                
                total_count = queryset.count()
                has_next = end < total_count
                
                return JsonResponse({
                    'success': True,
                    'lignes': lignes,
                    'count': len(lignes),
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'has_next': has_next,
                    'total_cdf': float(total_cdf),
                    'total_usd': float(total_usd),
                })
                
            elif type_etat in ['recette_du_mois', 'recette_par_banque', 'synthese_recettes']:
                # Utiliser la logique RECETTE_FEUILLE pour les nouveaux états
                queryset = RecetteFeuille.objects.all()
                print(f"Total initial RecetteFeuille: {queryset.count()}")
                
                # Récupérer les filtres selon le type d'état
                if type_etat == 'recette_du_mois':
                    mois = request.POST.get('mois_recette')
                    annee = request.POST.get('annee_recette')
                    print(f"Filtres recette du mois - Mois: {mois}, Année: {annee}")
                    
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                        
                elif type_etat == 'recette_par_banque':
                    mois = request.POST.get('mois_recette_banque')
                    annee = request.POST.get('annee_recette_banque')
                    banque = request.POST.get('banque_recette')
                    print(f"Filtres recette par banque - Mois: {mois}, Année: {annee}, Banque: {banque}")
                    
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    if banque and banque.isdigit() and banque != '':
                        queryset = queryset.filter(banque_id=int(banque))
                        
                elif type_etat == 'synthese_recettes':
                    mois = request.POST.get('mois_synthese_recettes')
                    annee = request.POST.get('annee_synthese_recettes')
                    print(f"Filtres synthèse recettes - Mois: {mois}, Année: {annee}")
                    
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                
                # Préparer les données pour la réponse
                lignes = []
                total_cdf = Decimal('0.00')
                total_usd = Decimal('0.00')
                
                # Pagination
                page = int(request.POST.get('page', 1))
                page_size = 50
                start = (page - 1) * page_size
                end = start + page_size
                
                queryset_paginated = queryset.order_by('-date')[start:end]
                
                for rec in queryset_paginated:
                    lignes.append({
                        'date': rec.date.strftime('%d/%m/%Y'),
                        'libelle_recette': rec.libelle_recette[:100],
                        'banque': rec.banque.nom_banque if rec.banque else '',
                        'montant_fc': float(rec.montant_fc),
                        'montant_usd': float(rec.montant_usd),
                    })
                    total_cdf += rec.montant_fc
                    total_usd += rec.montant_usd
                
                total_count = queryset.count()
                has_next = end < total_count
                
                return JsonResponse({
                    'success': True,
                    'lignes': lignes,
                    'count': len(lignes),
                    'total_count': total_count,
                    'page': page,
                    'page_size': page_size,
                    'has_next': has_next,
                    'total_cdf': float(total_cdf),
                    'total_usd': float(total_usd),
                })
                
            elif type_etat == 'DEPENSE_FEUILLE':
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
                
                # Limiter pour le preview (avec pagination)
                total_count = queryset.count()
                print(f"🔍 AVANT pagination: {total_count} résultats totaux")
                
                page = int(request.POST.get('page', 1))
                page_size = 50
                start = (page - 1) * page_size
                end = start + page_size
                
                print(f"📊 Pagination params: page={page}, start={start}, end={end}, page_size={page_size}")
                
                queryset = queryset.order_by('-date')[start:end]
                print(f"📊 Pagination: page {page}, {queryset.count()}/{total_count} résultats affichés")
                
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
                total_count = queryset.count()
                page = int(request.POST.get('page', 1))
                page_size = 50
                start = (page - 1) * page_size
                end = start + page_size
                
                queryset = queryset.order_by('-date')[start:end]
                print(f"📊 Pagination recettes: page {page}, {queryset.count()}/{total_count} résultats affichés")
                
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
                'total_count': total_count,  # Ajout du nombre total
                'page': page,
                'page_size': page_size,
                'has_next': end < total_count,
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
class EtatsFeuillesGenererView(View):
    """Vue pour générer les états feuilles"""
    
    def post(self, request, *args, **kwargs):
        try:
            format_sortie = request.POST.get('format_sortie', 'PDF')
            type_etat = request.POST.get('type_etat')
            type_rapport = request.POST.get('type_rapport', 'DETAILLE')  # DETAILLE, GROUPE, SYNTHESE
            
            print(f"Génération rapport: {type_etat}, format: {format_sortie}, type: {type_rapport}")
            
            # Gérer les nouveaux types d'état
            if type_etat in ['depense_par_nature', 'depense_par_mois', 'rapport_par_banque', 'synthese_par_banque', 'synthese_par_depenses']:
                return self._generer_pdf_nouveaux_etats(request, type_etat)
            elif type_etat in ['recette_du_mois', 'recette_par_banque', 'synthese_recettes']:
                return self._generer_pdf_nouveaux_etats(request, type_etat)
            
            if type_rapport == 'SYNTHESE':
                # Rapport synthétique - juste les totaux
                return self._generer_synthese(request, type_etat, format_sortie)
            elif type_rapport == 'GROUPE':
                # Rapport regroupé
                critere_groupement = request.POST.get('critere_groupement', 'nature')
                return self._generer_groupe(request, type_etat, critere_groupement, format_sortie)
            else:
                # Rapport détaillé (existant)
                if format_sortie == 'PDF':
                    if type_etat == 'RECETTE_FEUILLE':
                        return self._generer_pdf_recette_feuille(request)
                    elif type_etat == 'DEPENSE_FEUILLE':
                        return self._generer_pdf_depense_feuille(request)
                    else:
                        return JsonResponse({'success': True, 'etat_id': 'tableau_general_pdf'})
                else:
                    return JsonResponse({'success': False, 'error': 'Export Excel non encore implémenté'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _generer_pdf_nouveaux_etats(self, request, type_etat):
        """Générer un PDF pour les nouveaux types d'état"""
        try:
            if not REPORTLAB_AVAILABLE:
                return JsonResponse({'success': False, 'error': 'ReportLab non disponible. pip install reportlab'})
            from reportlab.lib.styles import ParagraphStyle
            styles_temp = getSampleStyleSheet()
            style_cell_libelle = ParagraphStyle('CellLibelleFlat', parent=styles_temp['Normal'], fontSize=8, leading=9)
            # Construire le queryset (même logique que preview)
            if type_etat in ['depense_par_nature', 'depense_par_mois', 'rapport_par_banque', 'synthese_par_banque', 'synthese_par_depenses']:
                queryset = DepenseFeuille.objects.all()
                if type_etat == 'depense_par_nature':
                    mois = request.POST.get('mois_nature')
                    annee = request.POST.get('annee_nature')
                    nature_filtre = request.POST.get('nature_economique')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    if nature_filtre and nature_filtre.isdigit() and nature_filtre != '':
                        queryset = queryset.filter(nature_economique_id=int(nature_filtre))
                    # Cas spécial : dépense par nature → regroupement par nature, nature en en-tête de groupe
                    return self._generer_pdf_depense_par_nature(request, queryset, mois, annee)
                elif type_etat == 'depense_par_mois':
                    mois = request.POST.get('mois_depense')
                    annee = request.POST.get('annee_mois')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                elif type_etat == 'rapport_par_banque':
                    mois = request.POST.get('mois_banque')
                    annee = request.POST.get('annee_banque')
                    banque_filtre = request.POST.get('banque_rapport')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    if banque_filtre and banque_filtre.isdigit() and banque_filtre != '':
                        queryset = queryset.filter(banque_id=int(banque_filtre))
                    return self._generer_pdf_rapport_par_banque(request, queryset, mois, annee)
                elif type_etat == 'synthese_par_banque':
                    mois = request.POST.get('mois_synthese_banque')
                    annee = request.POST.get('annee_synthese_banque')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    return self._generer_pdf_synthese_par_banque(request, queryset, mois, annee)
                elif type_etat == 'synthese_par_depenses':
                    mois = request.POST.get('mois_synthese_depenses')
                    annee = request.POST.get('annee_synthese_depenses')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                
                titre = 'DÉPENSES MENSUELLES' if type_etat == 'depense_par_mois' else 'ÉTAT DES DÉPENSES'
                queryset = queryset.order_by('-date')
                headers = ['Date', 'Libellé', 'Nature/Banque', 'Montant FC', 'Montant $us']
                def row_from_dep(dep):
                    lib_para = Paragraph(html.escape((dep.libelle_depenses or '')[:200]), style_cell_libelle)
                    return [
                        dep.date.strftime('%d/%m/%Y'),
                        lib_para,
                        (dep.nature_economique.titre if dep.nature_economique else '') or (dep.banque.nom_banque if dep.banque else ''),
                        f"{float(dep.montant_fc):,.2f}".replace(',', ' '),
                        f"{float(dep.montant_usd):,.2f}".replace(',', ' '),
                    ]
                rows = [row_from_dep(d) for d in queryset[:25]]
                
            elif type_etat in ['recette_du_mois', 'recette_par_banque', 'synthese_recettes']:
                queryset = RecetteFeuille.objects.all()
                if type_etat == 'recette_du_mois':
                    mois = request.POST.get('mois_recette')
                    annee = request.POST.get('annee_recette')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                elif type_etat == 'recette_par_banque':
                    mois = request.POST.get('mois_recette_banque')
                    annee = request.POST.get('annee_recette_banque')
                    banque = request.POST.get('banque_recette')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                    if banque and banque.isdigit() and banque != '':
                        queryset = queryset.filter(banque_id=int(banque))
                elif type_etat == 'synthese_recettes':
                    mois = request.POST.get('mois_synthese_recettes')
                    annee = request.POST.get('annee_synthese_recettes')
                    if annee and annee.isdigit() and annee != '':
                        queryset = queryset.filter(annee=int(annee))
                    if mois and mois.isdigit() and mois != '':
                        queryset = queryset.filter(mois=int(mois))
                
                titre = 'ÉTAT DES RECETTES'
                queryset = queryset.order_by('-date')
                headers = ['Date', 'Libellé', 'Banque', 'Montant FC', 'Montant $us']
                def row_from_rec(rec):
                    lib = (rec.libelle_recette or '')[:150]
                    ban = (rec.banque.nom_banque if rec.banque else '') or ''
                    return [
                        rec.date.strftime('%d/%m/%Y'),
                        lib,
                        ban,
                        f"{float(rec.montant_fc or 0):,.2f}".replace(',', ' '),
                        f"{float(rec.montant_usd or 0):,.2f}".replace(',', ' '),
                    ]
                rows = [row_from_rec(r) for r in queryset[:25]]
                
            else:
                return JsonResponse({'success': False, 'error': 'Type d\'état non valide'})
            
            # Calculer les totaux depuis le queryset
            total_fc = queryset.aggregate(s=Sum('montant_fc'))['s'] or Decimal('0')
            total_usd = queryset.aggregate(s=Sum('montant_usd'))['s'] or Decimal('0')
            
            # Générer le PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                rightMargin=0.5*cm, leftMargin=0.5*cm,
                topMargin=0.8*cm, bottomMargin=0.8*cm)
            styles = getSampleStyleSheet()
            elements = []
            # Logo du projet en en-tête (à gauche)
            logo_path = settings.BASE_DIR / 'static' / 'img' / 'logo_e-FinTrack.png'
            if logo_path.exists():
                logo = Image(str(logo_path), width=3*cm, height=1.5*cm)
                logo_table = Table([[logo]], colWidths=[3*cm])
                logo_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
                elements.append(logo_table)
                elements.append(Spacer(1, 0.3*cm))
            elements.append(Paragraph(titre, styles['Title']))
            # Ligne « Émis le / Période » au format reçu, pour tous les états simples
            mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                         'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            periode_label = 'Toutes périodes'
            if 'depense' in type_etat or 'synthese_par_depenses' in type_etat:
                # Période basée sur les filtres de dépenses
                if 'mois' in locals() and mois and str(mois).isdigit() and annee and str(annee).isdigit() and 1 <= int(mois) <= 12:
                    periode_label = f'{mois_noms[int(mois)].upper()} {annee}'
                elif 'annee' in locals() and annee and str(annee).isdigit():
                    periode_label = annee
            elif 'recette' in type_etat:
                # Période basée sur les filtres de recettes
                if 'mois' in locals() and mois and str(mois).isdigit() and annee and str(annee).isdigit() and 1 <= int(mois) <= 12:
                    periode_label = f'{mois_noms[int(mois)].upper()} {annee}'
                elif 'annee' in locals() and annee and str(annee).isdigit():
                    periode_label = annee
            date_emission = datetime.now().strftime('%d/%m/%Y %H:%M')
            col_widths = [2*cm, 14*cm, 4*cm, 4*cm, 4*cm]
            periode_row = [
                Paragraph(f'<b>Émis le : {date_emission}   |   Période : {periode_label}</b>', styles['Normal']),
                '', '', '', ''
            ]
            periode_table = Table([periode_row], colWidths=col_widths)
            periode_table.setStyle(TableStyle([
                ('SPAN', (0, 0), (-1, 0)),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#888888')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(periode_table)
            elements.append(Spacer(1, 0.3*cm))
            
            # En-têtes en majuscules comme dépense par nature
            headers_upper = [h.upper() for h in headers]
            table_data = [headers_upper] + rows
            if table_data:
                table = Table(table_data, colWidths=[2*cm, 14*cm, 4*cm, 4*cm, 4*cm])
                table.setStyle(TableStyle([
                    # En-tête en gris clair, texte noir
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dddddd')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    # Alignements
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('ALIGN', (1, 0), (2, -1), 'LEFT'),
                    ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    # Corps du tableau
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
                    # Bordures type reçu
                    ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.8, colors.black),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 0.3*cm))
                total_row = ['TOTAL', '', '', f"{float(total_fc):,.2f}".replace(',', ' '), f"{float(total_usd):,.2f}".replace(',', ' ')]
                total_table = Table([total_row], colWidths=[2*cm, 14*cm, 4*cm, 4*cm, 4*cm])
                total_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.8, colors.black),
                ]))
                elements.append(total_table)
            else:
                elements.append(Paragraph("Aucune donnée pour les critères sélectionnés.", styles['Normal']))
            doc.build(elements, onFirstPage=_footer_on_first, onLaterPages=_footer_on_later)
            pdf_value = buffer.getvalue()
            buffer.close()
            
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"etat_{type_etat}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            print(f"Erreur génération PDF: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _generer_pdf_depense_par_nature(self, request, queryset, mois, annee):
        """Générer PDF dépense par nature : nature au niveau du regroupement, pas dans les lignes détail"""
        try:
            from reportlab.lib.styles import ParagraphStyle
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                rightMargin=1.5*cm, leftMargin=1.5*cm,
                topMargin=1.5*cm, bottomMargin=1.5*cm)
            styles = getSampleStyleSheet()
            style_cell = ParagraphStyle('CellLibelle', parent=styles['Normal'], fontSize=8, leading=9)
            style_regroupement = ParagraphStyle('Regroupement', parent=styles['Heading2'], fontSize=9, leading=10)
            elements = []
            # Logo (à gauche)
            logo_path = settings.BASE_DIR / 'static' / 'img' / 'logo_e-FinTrack.png'
            if logo_path.exists():
                logo = Image(str(logo_path), width=3*cm, height=1.5*cm)
                logo_table = Table([[logo]], colWidths=[3*cm])
                logo_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
                elements.append(logo_table)
                elements.append(Spacer(1, 0.3*cm))
            mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                         'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            titre = 'ÉTAT DES DÉPENSES PAR ARTICLE LITTERA'
            elements.append(Paragraph(titre, styles['Title']))
            if annee and str(annee).isdigit():
                periode_label = f'{mois_noms[int(mois)].upper()} {annee}' if (mois and str(mois).isdigit() and 1 <= int(mois) <= 12) else annee
            else:
                periode_label = 'Toutes périodes'
            # Ligne de style reçu : Émis le + Période sur la même ligne
            date_emission = datetime.now().strftime('%d/%m/%Y %H:%M')
            col_widths = [2*cm, 14*cm, 4*cm, 4*cm, 4*cm]
            periode_row = [
                Paragraph(f'<b>Émis le : {date_emission}   |   Période : {periode_label}</b>', styles['Normal']),
                '', '', '', ''
            ]
            t_periode = Table([periode_row], colWidths=col_widths)
            t_periode.setStyle(TableStyle([
                ('SPAN', (0, 0), (-1, 0)),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                # Ligne de séparation épaisse grise sous l'en-tête
                ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#888888')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_periode)
            elements.append(Spacer(1, 0.3*cm))
            # Regroupement par nature
            groups = list(queryset.values('nature_economique_id', 'nature_economique__titre').annotate(
                total_cdf=Sum('montant_fc'), total_usd=Sum('montant_usd')
            ).order_by('nature_economique__titre'))
            headers_detail = ['DATE', 'LIBELLÉ', 'OBSERVATION', 'MONTANT FC', 'MONTANT $US']
            total_general_fc = Decimal('0')
            total_general_usd = Decimal('0')
            for idx, g in enumerate(groups):
                is_last = (idx == len(groups) - 1)
                nature_titre = g.get('nature_economique__titre') or 'Sans nature'
                depenses_groupe = queryset.filter(nature_economique_id=g['nature_economique_id']).order_by('-date')[:25]
                rows = []
                for d in depenses_groupe:
                    lib_text = html.escape((d.libelle_depenses or '')[:200])
                    lib_para = Paragraph(lib_text, style_cell)
                    rows.append([
                        d.date.strftime('%d/%m/%Y'),
                        lib_para,
                        (d.observation or '')[:50],
                        f"{float(d.montant_fc):,.2f}".replace(',', ' '),
                        f"{float(d.montant_usd):,.2f}".replace(',', ' '),
                    ])
                if rows:
                    # Nature en première ligne du tableau, même colonnes
                    nature_cell = Paragraph(f"<b>{nature_titre.upper()}</b>", style_regroupement)
                    table_data = [[nature_cell, '', '', '', '']] + [headers_detail] + rows
                    t = Table(table_data, colWidths=col_widths)
                    # Style type « reçu » : en-tête foncé, texte blanc, bordures nettes
                    t.setStyle(TableStyle([
                        # Ligne de titre de la nature (fond clair sur toute la ligne)
                        ('SPAN', (0, 0), (4, 0)),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        # En-tête du tableau (Date / Libellé / …) en gris clair
                        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#dddddd')),
                        ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
                        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 1), (-1, 1), 8),
                        # Alignements
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (2, -1), 'LEFT'),
                        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        # Corps de tableau
                        ('FONTSIZE', (0, 2), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 2), (-1, -1), 3),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        # Bordures type reçu
                        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.8, colors.black),
                    ]))
                    total_fc = g['total_cdf'] or Decimal('0')
                    total_usd = g['total_usd'] or Decimal('0')
                    total_general_fc += total_fc
                    total_general_usd += total_usd
                    total_row = ['TOTAL', '', '', f"{float(total_fc):,.2f}".replace(',', ' '), f"{float(total_usd):,.2f}".replace(',', ' ')]
                    tt = Table([total_row], colWidths=col_widths)
                    tt.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.8, colors.black),
                    ]))
                    if is_last:
                        grand_table = Table([['TOTAL GÉNÉRAL', '', '', f"{float(total_general_fc):,.2f}".replace(',', ' '), f"{float(total_general_usd):,.2f}".replace(',', ' ')]], colWidths=col_widths)
                        grand_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eeeeee')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        ]))
                        elements.append(KeepTogether([t, tt, Spacer(1, 0.3*cm), grand_table]))
                    else:
                        elements.append(t)
                        elements.append(tt)
                        elements.append(Spacer(1, 0.5*cm))
                else:
                    if is_last:
                        grand_table = Table([['TOTAL GÉNÉRAL', '', '', f"{float(total_general_fc):,.2f}".replace(',', ' '), f"{float(total_general_usd):,.2f}".replace(',', ' ')]], colWidths=col_widths)
                        grand_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eeeeee')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        ]))
                        elements.append(KeepTogether([Paragraph("Aucune dépense pour cette nature.", styles['Normal']), Spacer(1, 0.3*cm), grand_table]))
                    else:
                        elements.append(Paragraph("Aucune dépense pour cette nature.", styles['Normal']))
                    elements.append(Spacer(1, 0.5*cm))
            if not groups:
                grand_table = Table([['TOTAL GÉNÉRAL', '', '', '0,00', '0,00']], colWidths=col_widths)
                grand_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eeeeee')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                ]))
                elements.append(grand_table)
            doc.build(elements, onFirstPage=_footer_on_first, onLaterPages=_footer_on_later)
            pdf_value = buffer.getvalue()
            buffer.close()
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"etat_depense_par_nature_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            print(f"Erreur _generer_pdf_depense_par_nature: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _generer_pdf_rapport_par_banque(self, request, queryset, mois, annee):
        """Générer PDF rapport par banque : même structure que dépense par nature, regroupement par banque"""
        try:
            from reportlab.lib.styles import ParagraphStyle
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                rightMargin=1.5*cm, leftMargin=1.5*cm,
                topMargin=1.5*cm, bottomMargin=1.5*cm)
            styles = getSampleStyleSheet()
            style_cell = ParagraphStyle('CellLibelle', parent=styles['Normal'], fontSize=8, leading=9)
            style_regroupement = ParagraphStyle('Regroupement', parent=styles['Heading2'], fontSize=9, leading=10)
            elements = []
            logo_path = settings.BASE_DIR / 'static' / 'img' / 'logo_e-FinTrack.png'
            if logo_path.exists():
                logo = Image(str(logo_path), width=3*cm, height=1.5*cm)
                logo_table = Table([[logo]], colWidths=[3*cm])
                logo_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
                elements.append(logo_table)
                elements.append(Spacer(1, 0.3*cm))
            # Titre sans période (comme dépense par nature)
            titre = 'RAPPORT DES DÉPENSES PAR BANQUE'
            elements.append(Paragraph(titre, styles['Title']))
            # Ligne « Émis le / Période » au format reçu
            mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                         'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            if annee and str(annee).isdigit():
                periode_label = f'{mois_noms[int(mois)].upper()} {annee}' if (mois and str(mois).isdigit() and 1 <= int(mois) <= 12) else annee
            else:
                periode_label = 'Toutes périodes'
            date_emission = datetime.now().strftime('%d/%m/%Y %H:%M')
            col_widths = [2*cm, 14*cm, 4*cm, 4*cm, 4*cm]
            periode_row = [
                Paragraph(f'<b>Émis le : {date_emission}   |   Période : {periode_label}</b>', styles['Normal']),
                '', '', '', ''
            ]
            t_periode = Table([periode_row], colWidths=col_widths)
            t_periode.setStyle(TableStyle([
                ('SPAN', (0, 0), (-1, 0)),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#888888')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_periode)
            elements.append(Spacer(1, 0.3*cm))
            groups = list(queryset.values('banque_id', 'banque__nom_banque').annotate(
                total_cdf=Sum('montant_fc'), total_usd=Sum('montant_usd')
            ).order_by('banque__nom_banque'))
            headers_detail = ['DATE', 'LIBELLÉ', 'OBSERVATION', 'MONTANT FC', 'MONTANT $US']
            col_widths = [2*cm, 14*cm, 4*cm, 4*cm, 4*cm]
            total_general_fc = Decimal('0')
            total_general_usd = Decimal('0')
            for idx, g in enumerate(groups):
                is_last = (idx == len(groups) - 1)
                banque_titre = g.get('banque__nom_banque') or 'Sans banque'
                depenses_groupe = queryset.filter(banque_id=g['banque_id']).order_by('-date')[:25]
                rows = []
                for d in depenses_groupe:
                    lib_text = html.escape((d.libelle_depenses or '')[:200])
                    lib_para = Paragraph(lib_text, style_cell)
                    rows.append([
                        d.date.strftime('%d/%m/%Y'),
                        lib_para,
                        (d.observation or '')[:50],
                        f"{float(d.montant_fc):,.2f}".replace(',', ' '),
                        f"{float(d.montant_usd):,.2f}".replace(',', ' '),
                    ])
                if rows:
                    banque_cell = Paragraph(f"<b>{banque_titre.upper()}</b>", style_regroupement)
                    table_data = [[banque_cell, '', '', '', '']] + [headers_detail] + rows
                    t = Table(table_data, colWidths=col_widths)
                    # Reprendre exactement le style reçu de dépense par nature
                    t.setStyle(TableStyle([
                        # Ligne de titre de la banque (fond clair sur toute la ligne)
                        ('SPAN', (0, 0), (4, 0)),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f2f2f2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        # En-tête du tableau (DATE / LIBELLÉ / …) en gris clair
                        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#dddddd')),
                        ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
                        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 1), (-1, 1), 8),
                        # Alignements
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (2, -1), 'LEFT'),
                        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        # Corps de tableau
                        ('FONTSIZE', (0, 2), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 2), (-1, -1), 3),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        # Bordures type reçu
                        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.8, colors.black),
                    ]))
                    total_fc = g['total_cdf'] or Decimal('0')
                    total_usd = g['total_usd'] or Decimal('0')
                    total_general_fc += total_fc
                    total_general_usd += total_usd
                    total_row = ['TOTAL', '', '', f"{float(total_fc):,.2f}".replace(',', ' '), f"{float(total_usd):,.2f}".replace(',', ' ')]
                    tt = Table([total_row], colWidths=col_widths)
                    tt.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9f9f9')),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                        ('BOX', (0, 0), (-1, -1), 0.8, colors.black),
                    ]))
                    if is_last:
                        grand_table = Table([['TOTAL GÉNÉRAL', '', '', f"{float(total_general_fc):,.2f}".replace(',', ' '), f"{float(total_general_usd):,.2f}".replace(',', ' ')]], colWidths=col_widths)
                        grand_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eeeeee')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        ]))
                        elements.append(KeepTogether([t, tt, Spacer(1, 0.3*cm), grand_table]))
                    else:
                        elements.append(t)
                        elements.append(tt)
                        elements.append(Spacer(1, 0.5*cm))
                else:
                    if is_last:
                        grand_table = Table([['TOTAL GÉNÉRAL', '', '', f"{float(total_general_fc):,.2f}".replace(',', ' '), f"{float(total_general_usd):,.2f}".replace(',', ' ')]], colWidths=col_widths)
                        grand_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eeeeee')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                        ]))
                        elements.append(KeepTogether([Paragraph("Aucune dépense pour cette banque.", styles['Normal']), Spacer(1, 0.3*cm), grand_table]))
                    else:
                        elements.append(Paragraph("Aucune dépense pour cette banque.", styles['Normal']))
                    elements.append(Spacer(1, 0.5*cm))
            if not groups:
                grand_table = Table([['TOTAL GÉNÉRAL', '', '', '0,00', '0,00']], colWidths=col_widths)
                grand_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eeeeee')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
                ]))
                elements.append(grand_table)
            doc.build(elements, onFirstPage=_footer_on_first, onLaterPages=_footer_on_later)
            pdf_value = buffer.getvalue()
            buffer.close()
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"rapport_par_banque_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            print(f"Erreur _generer_pdf_rapport_par_banque: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _generer_pdf_synthese_par_banque(self, request, queryset, mois, annee):
        """Synthèse par banque : une ligne par banque (totaux) + total général. Filtres : mois et année uniquement."""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                rightMargin=1.5*cm, leftMargin=1.5*cm,
                topMargin=1.5*cm, bottomMargin=1.5*cm)
            styles = getSampleStyleSheet()
            elements = []
            logo_path = settings.BASE_DIR / 'static' / 'img' / 'logo_e-FinTrack.png'
            if logo_path.exists():
                logo = Image(str(logo_path), width=3*cm, height=1.5*cm)
                logo_table = Table([[logo]], colWidths=[3*cm])
                logo_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'LEFT')]))
                elements.append(logo_table)
                elements.append(Spacer(1, 0.3*cm))
            titre = 'SYNTHÈSE PAR BANQUE'
            elements.append(Paragraph(titre, styles['Title']))
            mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                         'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            if annee and str(annee).isdigit():
                if mois and str(mois).isdigit() and 1 <= int(mois) <= 12:
                    periode_label = f'{mois_noms[int(mois)]} {annee}'
                else:
                    periode_label = annee
            else:
                periode_label = 'Toutes périodes'
            col_widths = [12*cm, 6*cm, 6*cm]
            date_emission = datetime.now().strftime('%d/%m/%Y %H:%M')
            periode_row = [
                Paragraph(f'<b>Émis le : {date_emission}   |   Période : {periode_label}</b>', styles['Normal']),
                '', ''
            ]
            t_periode = Table([periode_row], colWidths=col_widths)
            t_periode.setStyle(TableStyle([
                ('SPAN', (0, 0), (-1, 0)),
                ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                # Ligne de séparation épaisse grise sous l'en-tête
                ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#888888')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t_periode)
            elements.append(Spacer(1, 0.3*cm))
            groups = list(queryset.values('banque_id', 'banque__nom_banque').annotate(
                total_cdf=Sum('montant_fc'), total_usd=Sum('montant_usd')
            ).order_by('banque__nom_banque'))
            headers = ['BANQUE', 'TOTAL FC', 'TOTAL $US']
            total_general_fc = Decimal('0')
            total_general_usd = Decimal('0')
            rows = []
            for g in groups:
                banque_nom = g.get('banque__nom_banque') or 'Sans banque'
                total_fc = g['total_cdf'] or Decimal('0')
                total_usd = g['total_usd'] or Decimal('0')
                total_general_fc += total_fc
                total_general_usd += total_usd
                rows.append([
                    banque_nom,
                    f"{float(total_fc):,.2f}".replace(',', ' '),
                    f"{float(total_usd):,.2f}".replace(',', ' '),
                ])
            table_data = [headers] + rows
            if table_data:
                t = Table(table_data, colWidths=col_widths)
                # Style type reçu : en-tête gris, texte foncé, bordures nettes
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dddddd')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.9, colors.black),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 0.3*cm))
                total_row = ['TOTAL GÉNÉRAL', f"{float(total_general_fc):,.2f}".replace(',', ' '), f"{float(total_general_usd):,.2f}".replace(',', ' ')]
                tt = Table([total_row], colWidths=col_widths)
                tt.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#222222')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.6, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.9, colors.black),
                ]))
                elements.append(tt)
            else:
                elements.append(Paragraph("Aucune donnée pour la période sélectionnée.", styles['Normal']))
            doc.build(elements, onFirstPage=_footer_on_first, onLaterPages=_footer_on_later)
            pdf_value = buffer.getvalue()
            buffer.close()
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"synthese_par_banque_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            print(f"Erreur _generer_pdf_synthese_par_banque: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': str(e)})
    
    def _generer_pdf_depense_feuille(self, request):
        """Générer PDF pour DEPENSE_FEUILLE (logique existante)"""
        # Implémenter la logique existante pour DEPENSE_FEUILLE
        return JsonResponse({'success': True, 'message': 'PDF DEPENSE_FEUILLE généré'})
    
    def _generer_pdf_recette_feuille(self, request):
        """Générer PDF pour RECETTE_FEUILLE (logique existante)"""
        # Implémenter la logique existante pour RECETTE_FEUILLE
        return JsonResponse({'success': True, 'message': 'PDF RECETTE_FEUILLE généré'})
    
    def _generer_synthese(self, request, type_etat, format_sortie):
        """Générer un rapport synthétique avec juste les totaux"""
        from decimal import Decimal
        from django.db.models import Sum, Q
        
        annee = request.POST.get('annee_depenses') or request.POST.get('annee_recettes')
        mois = request.POST.get('mois_depenses') or request.POST.get('mois_recettes')
        
        print(f"Synthèse - Année: {annee}, Mois: {mois}, Type: {type_etat}")
        
        # Construire les filtres
        filtres = Q()
        if annee and annee.isdigit() and annee != '':
            filtres &= Q(annee=int(annee))
        if mois and mois.isdigit() and mois != '':
            filtres &= Q(mois=int(mois))
        
        if type_etat == 'DEPENSE_FEUILLE':
            queryset = DepenseFeuille.objects.filter(filtres)
            resultats = queryset.aggregate(
                total_cdf=Sum('montant_fc'),
                total_usd=Sum('montant_usd'),
                nombre=Count('id')
            )
            titre = f"SYNTHÈSE DES DÉPENSES"
            if annee:
                titre += f" - {annee}"
            if mois and mois.isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                titre += f" - {mois_noms[int(mois)]}"
        else:
            queryset = RecetteFeuille.objects.filter(filtres)
            resultats = queryset.aggregate(
                total_cdf=Sum('montant_fc'),
                total_usd=Sum('montant_usd'),
                nombre=Count('id')
            )
            titre = f"SYNTHÈSE DES RECETTES"
            if annee:
                titre += f" - {annee}"
            if mois and mois.isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                titre += f" - {mois_noms[int(mois)]}"
        
        # Préparer les données pour le template
        data = {
            'titre': titre,
            'total_cdf': resultats['total_cdf'] or Decimal('0'),
            'total_usd': resultats['total_usd'] or Decimal('0'),
            'nombre': resultats['nombre'] or 0,
            'annee': annee,
            'mois': mois,
            'type_etat': type_etat
        }
        
        print(f"Données synthèse: {data}")
        
        if format_sortie == 'PDF':
            return JsonResponse({
                'success': True, 
                'type': 'SYNTHESE',
                'data': data
            })
        else:
            return JsonResponse({'success': False, 'error': 'Export Excel non encore implémenté'})
    
    def _generer_groupe(self, request, type_etat, critere_groupement, format_sortie):
        """Générer un rapport regroupé par critère"""
        from django.db.models import Sum, Count
        from collections import defaultdict
        
        annee = request.POST.get('annee_depenses') or request.POST.get('annee_recettes')
        mois = request.POST.get('mois_depenses') or request.POST.get('mois_recettes')
        
        print(f"Groupe - Critère: {critere_groupement}, Année: {annee}, Mois: {mois}, Type: {type_etat}")
        
        # Construire les filtres
        filtres = {}
        if annee and annee.isdigit() and annee != '':
            filtres['annee'] = int(annee)
        if mois and mois.isdigit() and mois != '':
            filtres['mois'] = int(mois)
        
        if type_etat == 'DEPENSE_FEUILLE':
            queryset = DepenseFeuille.objects.filter(**filtres)
            
            if critere_groupement == 'nature':
                groups = queryset.values('nature_economique__titre').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('nature_economique__titre')
                titre = f"DÉPENSES PAR NATURE ÉCONOMIQUE"
            elif critere_groupement == 'service':
                groups = queryset.values('service_beneficiaire__nom_service').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('service_beneficiaire__nom_service')
                titre = f"DÉPENSES PAR SERVICE BÉNÉFICIAIRE"
            elif critere_groupement == 'banque':
                groups = queryset.values('banque__nom_banque').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('banque__nom_banque')
                titre = f"DÉPENSES PAR BANQUE"
            elif critere_groupement == 'mois':
                groups = queryset.values('mois').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('mois')
                titre = f"DÉPENSES PAR MOIS"
            else:
                return JsonResponse({'success': False, 'error': 'Critère de regroupement non valide'})
                
        else:  # RECETTE_FEUILLE
            queryset = RecetteFeuille.objects.filter(**filtres)
            
            if critere_groupement == 'nature':
                groups = queryset.values('source_recette__nom').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('source_recette__nom')
                titre = f"RECETTES PAR SOURCE"
            elif critere_groupement == 'banque':
                groups = queryset.values('banque__nom_banque').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('banque__nom_banque')
                titre = f"RECETTES PAR BANQUE"
            elif critere_groupement == 'mois':
                groups = queryset.values('mois').annotate(
                    total_cdf=Sum('montant_fc'),
                    total_usd=Sum('montant_usd'),
                    nombre=Count('id')
                ).order_by('mois')
                titre = f"RECETTES PAR MOIS"
            else:
                return JsonResponse({'success': False, 'error': 'Critère de regroupement non valide pour les recettes'})
        
        # Ajouter la période au titre
        if annee:
            titre += f" - {annee}"
        if mois and mois.isdigit():
            mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                          'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
            titre += f" - {mois_noms[int(mois)]}"
        
        # Préparer les données
        data = {
            'titre': titre,
            'groups': list(groups),
            'critere': critere_groupement,
            'annee': annee,
            'mois': mois,
            'type_etat': type_etat
        }
        
        print(f"Données groupe: {len(data['groups'])} groupes trouvés")
        
        if format_sortie == 'PDF':
            return JsonResponse({
                'success': True, 
                'type': 'GROUPE',
                'data': data
            })
        else:
            return JsonResponse({'success': False, 'error': 'Export Excel non encore implémenté'})


@method_decorator(csrf_exempt, name='dispatch')
class RapportSynthesePDFView(LoginRequiredMixin, View):
    """Vue pour générer les rapports synthétiques en PDF"""
    
    def get(self, request, *args, **kwargs):
        if not REPORTLAB_AVAILABLE:
            return HttpResponse("ReportLab n'est pas disponible. Veuillez l'installer avec: pip install reportlab", content_type='text/plain')
        
        try:
            # Récupérer les données depuis l'URL
            from urllib.parse import unquote
            data_json = request.GET.get('data', '{}')
            data = json.loads(unquote(data_json))
            
            print(f"Génération PDF synthèse: {data}")
            
            # Créer le buffer PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                               rightMargin=1.5*cm, leftMargin=1.5*cm, 
                               topMargin=1.5*cm, bottomMargin=1.5*cm)
            
            styles = getSampleStyleSheet()
            elements = []
            
            # Titre
            titre_style = styles['Title']
            elements.append(Paragraph(data['titre'], titre_style))
            elements.append(Spacer(1, 0.5*cm))
            
            # Période
            periode = ""
            if data.get('annee'):
                periode = f"Année: {data['annee']}"
            if data.get('mois') and data['mois'].isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                periode += f" - {mois_noms[int(data['mois'])]}"
            
            if periode:
                elements.append(Paragraph(f"<b>Période:</b> {periode}", styles['Normal']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Statistiques principales
            elements.append(Paragraph("<b>STATISTIQUES PRINCIPALES</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.3*cm))
            
            # Convertir les montants en nombres
            try:
                total_cdf = float(data['total_cdf']) if data['total_cdf'] else 0
            except (ValueError, TypeError):
                total_cdf = 0
            
            try:
                total_usd = float(data['total_usd']) if data['total_usd'] else 0
            except (ValueError, TypeError):
                total_usd = 0
            
            stats_data = [
                ['Type', 'Nombre', 'Total CDF', 'Total USD'],
                [data['type_etat'].replace('_FEUILLE', '').capitalize(), 
                 str(data['nombre']), 
                 f"{total_cdf:,.2f}".replace(',', ' '), 
                 f"{total_usd:,.2f}".replace(',', ' ')]
            ]
            
            stats_table = Table(stats_data, colWidths=[4*cm, 3*cm, 5*cm, 5*cm])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 1*cm))
            
            # Générer le PDF
            doc.build(elements, onFirstPage=_footer_on_first, onLaterPages=_footer_on_later)
            
            # Préparer la réponse
            pdf_value = buffer.getvalue()
            buffer.close()
            
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"synthese_{data['type_etat'].lower()}_{data.get('annee', 'tout')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Erreur génération PDF synthèse: {e}")
            import traceback
            traceback.print_exc()
            return HttpResponse(f"Erreur: {str(e)}", content_type='text/plain')


@method_decorator(csrf_exempt, name='dispatch')
class RapportGroupePDFView(LoginRequiredMixin, View):
    """Vue pour générer les rapports regroupés en PDF"""
    
    def get(self, request, *args, **kwargs):
        if not REPORTLAB_AVAILABLE:
            return HttpResponse("ReportLab n'est pas disponible. Veuillez l'installer avec: pip install reportlab", content_type='text/plain')
        
        try:
            # Récupérer les données depuis l'URL
            from urllib.parse import unquote
            data_json = request.GET.get('data', '{}')
            data = json.loads(unquote(data_json))
            
            print(f"Génération PDF groupe: {data}")
            
            # Récupérer le type d'état dès le début
            type_etat = data.get('type_etat', 'DEPENSE_FEUILLE')
            
            # Définir le type de titre selon le type d'état
            titre_type = "Relevé des recettes" if type_etat == 'RECETTE_FEUILLE' else "Relevé des dépenses"
            
            # Créer le buffer PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                               rightMargin=1.5*cm, leftMargin=1.5*cm, 
                               topMargin=1.5*cm, bottomMargin=1.5*cm)
            
            styles = getSampleStyleSheet()
            elements = []
            
            # Titre personnalisé selon le critère
            critere = data['critere']
            # Adapter les libellés de critères selon le type d'état
            if type_etat == 'RECETTE_FEUILLE':
                critere_labels = {
                    'nature': 'Source de recette',
                    'service': 'Service Bénéficiaire', 
                    'banque': 'Banque',
                    'mois': 'Mois'
                }
            else:
                critere_labels = {
                    'nature': 'Article Littera',
                    'service': 'Service Bénéficiaire', 
                    'banque': 'Banque',
                    'mois': 'Mois'
                }
            
            titre = f"{titre_type} par {critere_labels.get(critere, critere)}"
            if data.get('mois') and data['mois'].isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                titre += f" du {mois_noms[int(data['mois'])]} {data.get('annee', '')}"
            elif data.get('annee'):
                titre += f" de l'année {data['annee']}"
            
            titre_style = styles['Title']
            elements.append(Paragraph(titre, titre_style))
            elements.append(Spacer(1, 0.5*cm))
            
            # Période
            periode = ""
            if data.get('annee'):
                periode = f"Année: {data['annee']}"
            if data.get('mois') and data['mois'].isdigit():
                mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                              'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                periode += f" - {mois_noms[int(data['mois'])]}"
            
            if periode:
                elements.append(Paragraph(f"<b>Période:</b> {periode}", styles['Normal']))
                elements.append(Spacer(1, 0.5*cm))
            
            # Importer les modèles selon le type d'état
            if type_etat == 'RECETTE_FEUILLE':
                from recettes.models import RecetteFeuille, SourceRecette
                from banques.models import Banque
                ModelFeuille = RecetteFeuille
            else:
                from demandes.models import DepenseFeuille, NatureEconomique, Service
                from banques.models import Banque
                ModelFeuille = DepenseFeuille
            
            # Traiter chaque regroupement avec détails
            groups = data['groups']
            
            for group in groups:
                # Récupérer le libellé du regroupement selon le type d'état
                if critere == 'nature':
                    if type_etat == 'RECETTE_FEUILLE':
                        groupe_libelle = str(group.get('source_recette__nom', 'N/A'))
                        groupe_id = group.get('source_recette_id')
                    else:
                        groupe_libelle = str(group.get('nature_economique__titre', 'N/A'))
                        groupe_id = group.get('nature_economique_id')
                elif critere == 'service':
                    # Pour les recettes, le service n'est pas applicable
                    if type_etat == 'RECETTE_FEUILLE':
                        continue  # Skip ce groupe pour les recettes
                    groupe_libelle = str(group.get('service_beneficiaire__nom_service', 'N/A'))
                    groupe_id = group.get('service_beneficiaire_id')
                elif critere == 'banque':
                    groupe_libelle = str(group.get('banque__nom_banque', 'N/A'))
                    groupe_id = group.get('banque_id')
                elif critere == 'mois':
                    mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                    mois_num = group.get('mois', 0)
                    groupe_libelle = mois_noms[mois_num] if mois_num < len(mois_noms) else f"Mois {mois_num}"
                    groupe_id = mois_num
                else:
                    continue
                
                # Afficher le libellé du regroupement
                elements.append(Paragraph(f"<b>{groupe_libelle.upper()}</b>", styles['Heading2']))
                elements.append(Spacer(1, 0.3*cm))
                
                # Récupérer les données détaillées pour ce regroupement
                donnees = ModelFeuille.objects.all()
                
                # Filtrer par période
                if data.get('annee'):
                    donnees = donnees.filter(annee=data['annee'])
                if data.get('mois') and data['mois'].isdigit():
                    donnees = donnees.filter(mois=int(data['mois']))
                
                # Filtrer par critère de regroupement selon le type d'état
                if critere == 'nature' and groupe_id:
                    if type_etat == 'RECETTE_FEUILLE':
                        donnees = donnees.filter(source_recette_id=groupe_id)
                    else:
                        donnees = donnees.filter(nature_economique_id=groupe_id)
                elif critere == 'service' and groupe_id:
                    donnees = donnees.filter(service_beneficiaire_id=groupe_id)
                elif critere == 'banque' and groupe_id:
                    donnees = donnees.filter(banque_id=groupe_id)
                elif critere == 'mois' and groupe_id:
                    donnees = donnees.filter(mois=groupe_id)
                
                # Préparer les données du tableau détaillé selon le type
                if type_etat == 'RECETTE_FEUILLE':
                    headers = ['Date', 'Libellé recette', 'Montant CDF', 'Montant USD']
                else:
                    headers = ['Date', 'Libellé dépense', 'Montant CDF', 'Montant USD']
                table_data = [headers]
                
                total_cdf_groupe = 0
                total_usd_groupe = 0
                
                for item in donnees.order_by('date'):
                    montant_cdf = item.montant_fc or 0
                    montant_usd = item.montant_usd or 0
                    
                    total_cdf_groupe += montant_cdf
                    total_usd_groupe += montant_usd
                    
                    # Adapter le libellé selon le type (augmenter la longueur)
                    if type_etat == 'RECETTE_FEUILLE':
                        libelle = item.libelle_recette[:150]
                    else:
                        libelle = item.libelle_depenses[:150]
                    
                    table_data.append([
                        item.date.strftime('%d/%m/%Y'),
                        libelle,
                        f"{montant_cdf:,.2f}".replace(',', ' ') if montant_cdf > 0 else '0,00',
                        f"{montant_usd:,.2f}".replace(',', ' ') if montant_usd > 0 else '0,00'
                    ])
                
                # Créer le tableau détaillé
                if len(table_data) > 1:  # S'il y a des dépenses
                    table = Table(table_data, colWidths=[2.5*cm, 10*cm, 4.5*cm, 4.5*cm])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('FONTSIZE', (0, 1), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    
                    elements.append(table)
                    elements.append(Spacer(1, 0.3*cm))
                    
                    # Afficher le total du groupe
                    total_data = [
                        ['TOTAL', '', 
                         f"{total_cdf_groupe:,.2f}".replace(',', ' '), 
                         f"{total_usd_groupe:,.2f}".replace(',', ' ')]
                    ]
                    
                    total_table = Table(total_data, colWidths=[2.5*cm, 10*cm, 4.5*cm, 4.5*cm])
                    total_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP')
                    ]))
                    
                    elements.append(total_table)
                else:
                    # Aucune dépense pour ce regroupement
                    elements.append(Paragraph("Aucune dépense trouvée pour ce regroupement.", styles['Normal']))
                
                # Saut de page entre les regroupements (sauf pour le dernier)
                elements.append(Spacer(1, 1*cm))
            
            # Générer le PDF
            doc.build(elements, onFirstPage=_footer_on_first, onLaterPages=_footer_on_later)
            
            # Préparer la réponse
            pdf_value = buffer.getvalue()
            buffer.close()
            
            response = HttpResponse(pdf_value, content_type='application/pdf')
            filename = f"rapport_groupe_{data['critere']}_{data.get('annee', 'tout')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Erreur génération PDF groupe: {e}")
            import traceback
            traceback.print_exc()
            return HttpResponse(f"Erreur: {str(e)}", content_type='text/plain')


class NaturesEconomiquesAPIView(View):
    """Vue API pour récupérer la liste des natures économiques"""
    
    def get(self, request, *args, **kwargs):
        try:
            from demandes.models import NatureEconomique
            
            # Récupérer toutes les natures économiques actives
            natures = NatureEconomique.objects.filter(active=True).order_by('code')
            
            # Préparer les données pour le select
            data = []
            for nature in natures:
                data.append({
                    'id': nature.id,
                    'code': nature.code,
                    'titre': nature.titre,
                    'display': f"{nature.code} - {nature.titre}"
                })
            
            return JsonResponse({
                'success': True,
                'natures': data
            })
            
        except Exception as e:
            print(f"Erreur dans NaturesEconomiquesAPIView: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})


class BanquesAPIView(View):
    """Vue API pour récupérer la liste des banques"""
    
    def get(self, request, *args, **kwargs):
        try:
            from banques.models import Banque
            
            # Récupérer toutes les banques actives
            banques = Banque.objects.filter(active=True).order_by('nom_banque')
            
            # Préparer les données pour le select
            data = []
            for banque in banques:
                data.append({
                    'id': banque.id,
                    'nom_banque': banque.nom_banque,
                    'display': banque.nom_banque
                })
            
            return JsonResponse({
                'success': True,
                'banques': data
            })
            
        except Exception as e:
            print(f"Erreur dans BanquesAPIView: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
