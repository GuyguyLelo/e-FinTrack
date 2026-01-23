"""
Vues pour les rapports et le tableau de bord
"""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from banques.models import Banque, CompteBancaire
from demandes.models import DemandePaiement, ReleveDepense, Depense, Paiement, Paiement
from recettes.models import Recette
from releves.models import ReleveBancaire, MouvementBancaire
from rapprochements.models import RapprochementBancaire

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Tableau de bord principal avec statistiques consolidées"""
    template_name = 'rapports/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Gérer la requête avec gestion d'erreur pour éviter les problèmes de session"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            # Vérifier si c'est une erreur de session interrompue
            is_session_error = (
                'SessionInterrupted' in str(type(e).__name__) or
                'session' in str(e).lower() and 'deleted' in str(e).lower() or
                'SessionInterrupted' in str(e)
            )
            
            if is_session_error:
                logger.warning(f"Session interrompue dans DashboardView: {str(e)}")
                # Le middleware devrait gérer cela, mais on fait un fallback ici
                from django.http import HttpResponseRedirect
                from django.urls import reverse
                try:
                    return HttpResponseRedirect(reverse('accounts:login') + '?session_expired=1')
                except Exception:
                    return HttpResponseRedirect('/accounts/login/?session_expired=1')
            
            # Logger les autres erreurs pour le débogage
            logger.error(f"Erreur dans DashboardView: {str(e)}", exc_info=True)
            # Ne pas utiliser messages ici car la session peut être déjà interrompue
            # Rediriger vers la page de login en cas d'erreur grave
            from django.contrib.auth import logout
            try:
                logout(request)
            except Exception:
                pass
            from django.shortcuts import redirect
            from django.urls import reverse
            try:
                return redirect(reverse('accounts:login'))
            except Exception:
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect('/accounts/login/')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Période par défaut : mois en cours
            now = timezone.now()
            mois_courant = now.month
            annee_courante = now.year
            
            # Statistiques globales
            context['total_banques'] = Banque.objects.filter(active=True).count()
            context['total_comptes'] = CompteBancaire.objects.filter(actif=True).count()
            
            # Solde consolidé par devise : calculé à partir de toutes les recettes moins les paiements effectués
            # Total de toutes les recettes (validées ou non, toutes périodes confondues)
            total_recettes_usd = Recette.objects.filter(
                montant_usd__gt=0
            ).aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
            
            total_recettes_cdf = Recette.objects.filter(
                montant_cdf__gt=0
            ).aggregate(total=Sum('montant_cdf'))['total'] or Decimal('0.00')
            
            # Total des paiements effectués (pour déduire des recettes)
            total_paiements_usd = Paiement.objects.filter(
                devise='USD'
            ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0.00')
            
            total_paiements_cdf = Paiement.objects.filter(
                devise='CDF'
            ).aggregate(total=Sum('montant_paye'))['total'] or Decimal('0.00')
            
            # Solde consolidé = Recettes validées - Paiements effectués
            solde_usd = total_recettes_usd - total_paiements_usd
            solde_cdf = total_recettes_cdf - total_paiements_cdf
            
            context['solde_consolide_usd'] = float(solde_usd)  # Convertir en float pour le template
            context['solde_consolide_cdf'] = float(solde_cdf)  # Convertir en float pour le template
            
            # Demandes de paiement
            context['total_demandes'] = DemandePaiement.objects.count()
            context['demandes_en_attente'] = DemandePaiement.objects.filter(statut='EN_ATTENTE').count()
            context['demandes_validees'] = DemandePaiement.objects.filter(statut__in=['VALIDEE_DG', 'VALIDEE_DF']).count()
            context['demandes_payees'] = DemandePaiement.objects.filter(statut='PAYEE').count()
            
            # Recettes du mois
            recettes_mois_usd = Recette.objects.filter(
                valide=True,
                montant_usd__gt=0,
                date_encaissement__year=annee_courante,
                date_encaissement__month=mois_courant
            ).aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
            
            recettes_mois_cdf = Recette.objects.filter(
                valide=True,
                montant_cdf__gt=0,
                date_encaissement__year=annee_courante,
                date_encaissement__month=mois_courant
            ).aggregate(total=Sum('montant_cdf'))['total'] or Decimal('0.00')
            
            context['recettes_mois_usd'] = float(recettes_mois_usd)  # Convertir en float
            context['recettes_mois_cdf'] = float(recettes_mois_cdf)  # Convertir en float
            
            # Dépenses du mois (uniquement les dépenses validées via les relevés)
            depenses_mois = Depense.objects.filter(
                annee=annee_courante,
                mois=mois_courant
            )
            
            depenses_mois_usd = depenses_mois.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
            depenses_mois_cdf = depenses_mois.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
            
            context['depenses_mois_usd'] = float(depenses_mois_usd)  # Convertir en float
            context['depenses_mois_cdf'] = float(depenses_mois_cdf)  # Convertir en float
            
            # Relevés bancaires
            context['releves_valides'] = ReleveBancaire.objects.filter(valide=True).count()
            context['releves_en_attente'] = ReleveBancaire.objects.filter(valide=False).count()
            
            # Rapprochements
            context['rapprochements_valides'] = RapprochementBancaire.objects.filter(valide=True).count()
            context['rapprochements_en_attente'] = RapprochementBancaire.objects.filter(valide=False).count()
            
            # Graphiques - Données pour les 12 derniers mois
            mois_list = []
            recettes_usd_list = []
            recettes_cdf_list = []
            depenses_usd_list = []
            depenses_cdf_list = []
            
            for i in range(11, -1, -1):
                date = now - timedelta(days=30 * i)
                mois_annee = date.strftime('%Y-%m')
                mois_nom = date.strftime('%b %Y')
                mois_list.append(mois_nom)
                
                # Recettes
                rec_usd = Recette.objects.filter(
                    valide=True,
                    montant_usd__gt=0,
                    date_encaissement__year=date.year,
                    date_encaissement__month=date.month
                ).aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
                
                rec_cdf = Recette.objects.filter(
                    valide=True,
                    montant_cdf__gt=0,
                    date_encaissement__year=date.year,
                    date_encaissement__month=date.month
                ).aggregate(total=Sum('montant_cdf'))['total'] or Decimal('0.00')
                
                recettes_usd_list.append(float(rec_usd))
                recettes_cdf_list.append(float(rec_cdf))
                
                # Dépenses (uniquement les dépenses validées via les relevés)
                dep_usd = Depense.objects.filter(
                    annee=date.year,
                    mois=date.month,
                    montant_usd__gt=0
                ).aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
                
                dep_cdf = Depense.objects.filter(
                    annee=date.year,
                    mois=date.month,
                    montant_fc__gt=0
                ).aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
                
                depenses_usd_list.append(float(dep_usd))
                depenses_cdf_list.append(float(dep_cdf))
            
            import json
            context['mois_labels'] = json.dumps(mois_list)
            context['recettes_usd_data'] = json.dumps(recettes_usd_list)
            context['recettes_cdf_data'] = json.dumps(recettes_cdf_list)
            context['depenses_usd_data'] = json.dumps(depenses_usd_list)
            context['depenses_cdf_data'] = json.dumps(depenses_cdf_list)
            
            # Solde par banque
            banques_data = []
            for banque in Banque.objects.filter(active=True):
                comptes = banque.comptes.filter(actif=True)
                solde_usd = sum(c.solde_courant for c in comptes.filter(devise='USD'))
                solde_cdf = sum(c.solde_courant for c in comptes.filter(devise='CDF'))
                
                # Ajouter toutes les banques actives, même avec solde nul pour le graphique
                banques_data.append({
                    'nom': banque.nom_banque,
                    'solde_usd': float(solde_usd),
                    'solde_cdf': float(solde_cdf),
                })
            
            # Filtrer pour le tableau (uniquement les banques avec solde > 0)
            banques_avec_solde = [b for b in banques_data if b['solde_usd'] > 0 or b['solde_cdf'] > 0]
            
            import json
            context['banques_data'] = json.dumps(banques_data)  # Pour le graphique
            context['banques_avec_solde'] = banques_avec_solde  # Pour le tableau
            
            # Recettes récentes (10 dernières)
            context['recettes_recentes'] = Recette.objects.select_related(
                'banque', 'compte_bancaire', 'enregistre_par', 'valide_par'
            ).order_by('-date_encaissement', '-date_creation')[:10]
            
            # Dépenses récentes (10 dernières)
            context['depenses_recentes'] = Depense.objects.select_related(
                'banque', 'nomenclature'
            ).order_by('-date_depense', '-annee', '-mois')[:10]
            
        except Exception as e:
            # Logger l'erreur mais continuer avec des valeurs par défaut
            logger.error(f"Erreur lors du chargement des données du dashboard: {str(e)}", exc_info=True)
            # Valeurs par défaut pour éviter une erreur dans le template
            context.setdefault('total_banques', 0)
            context.setdefault('total_comptes', 0)
            context.setdefault('solde_consolide_usd', 0.0)
            context.setdefault('solde_consolide_cdf', 0.0)
            context.setdefault('total_demandes', 0)
            context.setdefault('demandes_en_attente', 0)
            context.setdefault('demandes_validees', 0)
            context.setdefault('demandes_payees', 0)
            context.setdefault('recettes_mois_usd', 0.0)
            context.setdefault('recettes_mois_cdf', 0.0)
            context.setdefault('depenses_mois_usd', 0.0)
            context.setdefault('depenses_mois_cdf', 0.0)
            context.setdefault('releves_valides', 0)
            context.setdefault('releves_en_attente', 0)
            context.setdefault('rapprochements_valides', 0)
            context.setdefault('rapprochements_en_attente', 0)
            import json
            context.setdefault('mois_labels', json.dumps([]))
            context.setdefault('recettes_usd_data', json.dumps([]))
            context.setdefault('recettes_cdf_data', json.dumps([]))
            context.setdefault('depenses_usd_data', json.dumps([]))
            context.setdefault('depenses_cdf_data', json.dumps([]))
            context.setdefault('banques_data', json.dumps([]))
            context.setdefault('recettes_recentes', [])
            context.setdefault('depenses_recentes', [])
        
        return context


class RapportConsolideView(LoginRequiredMixin, TemplateView):
    """Rapport consolidé détaillé"""
    template_name = 'rapports/rapport_consolide.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Filtrer par période si fournie
        annee = self.request.GET.get('annee', timezone.now().year)
        mois = self.request.GET.get('mois')
        
        try:
            annee = int(annee)
            if mois:
                mois = int(mois)
        except (ValueError, TypeError):
            annee = timezone.now().year
            mois = None
        
        context['annee'] = annee
        context['mois'] = mois
        
        # Recettes
        recettes_qs = Recette.objects.filter(valide=True, date_encaissement__year=annee)
        if mois:
            recettes_qs = recettes_qs.filter(date_encaissement__month=mois)
        
        context['total_recettes_usd'] = recettes_qs.aggregate(
            total=Sum('montant_usd')
        )['total'] or Decimal('0.00')
        
        context['total_recettes_cdf'] = recettes_qs.aggregate(
            total=Sum('montant_cdf')
        )['total'] or Decimal('0.00')
        
        # Dépenses (uniquement les demandes de paiement validées)
        depenses_qs = DemandePaiement.objects.filter(
            statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE'],
            date_soumission__year=annee
        )
        if mois:
            depenses_qs = depenses_qs.filter(date_soumission__month=mois)
        
        context['total_depenses_usd'] = depenses_qs.filter(
            devise='USD'
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
        
        context['total_depenses_cdf'] = depenses_qs.filter(
            devise='CDF'
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
        
        # Évolution des 12 derniers mois
        evolution_data = []
        for i in range(12):
            date_mois = timezone.now() - timedelta(days=30*i)
            mois_evol = date_mois.month
            annee_evol = date_mois.year
            
            recettes_mois = Recette.objects.filter(
                valide=True,
                date_encaissement__year=annee_evol,
                date_encaissement__month=mois_evol
            )
            
            depenses_mois = DemandePaiement.objects.filter(
                statut__in=['VALIDEE_DG', 'VALIDEE_DF', 'PAYEE'],
                date_soumission__year=annee_evol,
                date_soumission__month=mois_evol
            )
            
            evolution_data.append({
                'mois': date_mois.strftime('%Y-%m'),
                'libelle': date_mois.strftime('%b %Y'),
                'recettes_usd': recettes_mois.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00'),
                'recettes_cdf': recettes_mois.aggregate(total=Sum('montant_cdf'))['total'] or Decimal('0.00'),
                'depenses_usd': depenses_mois.filter(devise='USD').aggregate(total=Sum('montant'))['total'] or Decimal('0.00'),
                'depenses_cdf': depenses_mois.filter(devise='CDF').aggregate(total=Sum('montant'))['total'] or Decimal('0.00'),
            })
        
        context['evolution_data'] = evolution_data
        
        # Détails par banque
        banques_details = []
        for banque in Banque.objects.filter(active=True):
            comptes = banque.comptes.filter(actif=True)
            recettes_banque = recettes_qs.filter(banque=banque)
            
            # Pour les dépenses, on utilise les demandes validées (sans lien direct avec banque)
            # On affiche les totaux généraux pour toutes les banques
            depenses_usd_total = depenses_qs.filter(devise='USD').aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
            depenses_cdf_total = depenses_qs.filter(devise='CDF').aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
            
            banques_details.append({
                'banque': banque,
                'recettes_usd': sum(r.montant_usd for r in recettes_banque),
                'recettes_cdf': sum(r.montant_cdf for r in recettes_banque),
                'depenses_usd': depenses_usd_total / len(Banque.objects.filter(active=True)) if len(Banque.objects.filter(active=True)) > 0 else Decimal('0.00'),
                'depenses_cdf': depenses_cdf_total / len(Banque.objects.filter(active=True)) if len(Banque.objects.filter(active=True)) > 0 else Decimal('0.00'),
            })
        
        context['banques_details'] = banques_details
        
        return context

