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

from accounts.permissions import RoleRequiredMixin

from banques.models import Banque, CompteBancaire
from demandes.models import DemandePaiement, ReleveDepense, Depense, Paiement
from recettes.models import Recette
from releves.models import ReleveBancaire, MouvementBancaire

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Tableau de bord principal avec statistiques consolidées"""
    template_name = 'rapports/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Gérer la requête avec gestion d'erreur pour éviter les problèmes de session"""
        try:
            # Vérifier si l'utilisateur a la permission de voir le tableau de bord
            if hasattr(request.user, 'rbac_role') and request.user.rbac_role:
                if hasattr(request.user, 'has_rbac_permission'):
                    if not request.user.has_rbac_permission('voir_tableau_bord'):
                        # Utilisateur RBAC sans permission tableau de bord -> rediriger vers l'accueil
                        # Éviter la boucle de redirection : ne pas rediriger si déjà sur /
                        if request.path != '/':
                            from django.shortcuts import redirect
                            return redirect('/')
            
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
                return redirect('/accounts/login/')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        try:
            # Période par défaut : mois en cours
            now = timezone.now()
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            context.update({
                'start_date': start_date,
                'end_date': end_date,
                'period_display': f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
            })
            
            # Statistiques générales
            stats = self.get_general_stats(start_date, end_date)
            context.update(stats)
            
            # Données pour graphiques
            chart_data = self.get_chart_data(start_date, end_date)
            context.update(chart_data)
            
            # Dernières activités
            recent_activities = self.get_recent_activities()
            context['recent_activities'] = recent_activities
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation des données du dashboard: {str(e)}", exc_info=True)
            context['error'] = "Une erreur est survenue lors du chargement des données"
        
        return context
    
    def get_general_stats(self, start_date, end_date):
        """Obtenir les statistiques générales synchronisées avec le tableau de bord DAF"""
        try:
            from demandes.models import DepenseFeuille
            from recettes.models import RecetteFeuille
            from clotures.models import ClotureMensuelle
            from django.utils.timezone import now
            
            # Période actuelle (similaire au tableau de bord DAF)
            today = now()
            current_year = today.year
            current_month = today.month
            
            # Récupérer la période actuelle
            try:
                periode_actuelle = ClotureMensuelle.get_periode_actuelle()
                periode_actuelle.calculer_soldes()
                periode_actuelle.refresh_from_db()
            except:
                periode_actuelle = ClotureMensuelle.objects.create(
                    mois=current_month,
                    annee=current_year,
                    statut='OUVERT',
                    solde_ouverture_fc=0,
                    solde_ouverture_usd=0
                )
            
            # Statistiques des banques (identiques au DAF)
            banques_count = Banque.objects.count()
            comptes_count = CompteBancaire.objects.count()
            
            # Statistiques des dépenses (utilisant DepenseFeuille comme DAF)
            depenses = DepenseFeuille.objects.filter(
                mois=periode_actuelle.mois,
                annee=periode_actuelle.annee
            )
            depenses_count = depenses.count()
            
            total_depenses_cdf = depenses.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
            total_depenses_usd = depenses.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
            depenses_total = total_depenses_cdf  # Pour compatibilité
            
            # Statistiques des recettes (utilisant RecetteFeuille comme DAF)
            recettes = RecetteFeuille.objects.filter(
                mois=periode_actuelle.mois,
                annee=periode_actuelle.annee
            )
            recettes_count = recettes.count()
            
            total_recettes_cdf = recettes.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
            total_recettes_usd = recettes.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
            recettes_total = total_recettes_cdf  # Pour compatibilité
            
            # Solde net (identique au DAF)
            solde_cdf = total_recettes_cdf - total_depenses_cdf
            solde_usd = total_recettes_usd - total_depenses_usd
            
            # Statistiques des demandes (garder l'original)
            demandes_count = DemandePaiement.objects.filter(
                date_demande__range=(start_date, end_date)
            ).count()
            
            demandes_total = DemandePaiement.objects.filter(
                date_demande__range=(start_date, end_date)
            ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
            
            return {
                'banques_count': banques_count,
                'comptes_count': comptes_count,
                'depenses_count': depenses_count,
                'depenses_total': depenses_total,
                'total_depenses_cdf': total_depenses_cdf,
                'total_depenses_usd': total_depenses_usd,
                'recettes_count': recettes_count,
                'recettes_total': recettes_total,
                'total_recettes_cdf': total_recettes_cdf,
                'total_recettes_usd': total_recettes_usd,
                'solde_cdf': solde_cdf,
                'solde_usd': solde_usd,
                'demandes_count': demandes_count,
                'demandes_total': demandes_total,
                'periode_actuelle': periode_actuelle,
                'solde_net': recettes_total - depenses_total,
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques générales: {str(e)}", exc_info=True)
            return {}
    
    def get_chart_data(self, start_date, end_date):
        """Préparer les données pour les graphiques synchronisées avec le tableau de bord DAF"""
        try:
            from demandes.models import DepenseFeuille
            from recettes.models import RecetteFeuille
            from clotures.models import ClotureMensuelle
            from django.utils.timezone import now
            
            # Période actuelle (similaire au DAF)
            today = now()
            current_year = today.year
            
            # Données mensuelles pour l'année actuelle (similaire au DAF)
            chart_data = []
            
            for mois in range(1, 13):
                month_depenses = DepenseFeuille.objects.filter(
                    annee=current_year,
                    mois=mois
                ).aggregate(total_fc=Sum('montant_fc'), total_usd=Sum('montant_usd'))
                
                month_recettes = RecetteFeuille.objects.filter(
                    annee=current_year,
                    mois=mois
                ).aggregate(total_fc=Sum('montant_fc'), total_usd=Sum('montant_usd'))
                
                depenses_total = (month_depenses['total_fc'] or Decimal('0.00')) + (month_depenses['total_usd'] or Decimal('0.00'))
                recettes_total = (month_recettes['total_fc'] or Decimal('0.00')) + (month_recettes['total_usd'] or Decimal('0.00'))
                
                chart_data.append({
                    'month': f"{today.replace(day=1, month=mois).strftime('%b')} {current_year}",
                    'depenses': float(depenses_total),
                    'recettes': float(recettes_total),
                    'solde': float(recettes_total - depenses_total)
                })
            
            return {
                'chart_data': chart_data,
                'chart_labels': [item['month'] for item in chart_data]
            }
        except Exception as e:
            logger.error(f"Erreur lors de la préparation des données de graphique: {str(e)}", exc_info=True)
            return {'chart_data': [], 'chart_labels': []}
    
    def get_recent_activities(self):
        """Obtenir les dernières activités synchronisées avec le tableau de bord DAF"""
        try:
            from demandes.models import DepenseFeuille
            from recettes.models import RecetteFeuille
            from clotures.models import ClotureMensuelle
            from django.utils.timezone import now
            
            # Période actuelle
            today = now()
            current_year = today.year
            current_month = today.month
            
            # Récupérer la période actuelle
            try:
                periode_actuelle = ClotureMensuelle.get_periode_actuelle()
            except:
                periode_actuelle = ClotureMensuelle.objects.create(
                    mois=current_month,
                    annee=current_year,
                    statut='OUVERT',
                    solde_ouverture_fc=0,
                    solde_ouverture_usd=0
                )
            
            # Activités des feuilles DAF (similaire au tableau de bord DAF)
            recent_depenses_feuilles = DepenseFeuille.objects.filter(
                mois=periode_actuelle.mois,
                annee=periode_actuelle.annee
            ).order_by('-date_creation')[:5]
            
            recent_recettes_feuilles = RecetteFeuille.objects.filter(
                mois=periode_actuelle.mois,
                annee=periode_actuelle.annee
            ).order_by('-date_creation')[:5]
            
            # Garder aussi les demandes de paiement pour le système WICKFLOW
            recent_demandes = DemandePaiement.objects.order_by('-date_demande')[:3]
            
            activities = []
            
            # Ajouter les activités des feuilles de dépenses
            for depense in recent_depenses_feuilles:
                total_montant = (depense.montant_fc or Decimal('0.00')) + (depense.montant_usd or Decimal('0.00'))
                activities.append({
                    'type': 'depense_feuille',
                    'description': f"Dépense feuille: {depense.libelle_depenses or 'Sans libellé'}",
                    'date': depense.date_creation.strftime('%d/%m/%Y %H:%M'),
                    'montant': float(total_montant),
                    'banque': depense.banque.nom_banque if depense.banque else 'Non spécifiée'
                })
            
            # Ajouter les activités des feuilles de recettes
            for recette in recent_recettes_feuilles:
                total_montant = (recette.montant_fc or Decimal('0.00')) + (recette.montant_usd or Decimal('0.00'))
                activities.append({
                    'type': 'recette_feuille',
                    'description': f"Recette feuille: {recette.description or 'Sans description'}",
                    'date': recette.date_creation.strftime('%d/%m/%Y %H:%M'),
                    'montant': float(total_montant),
                    'banque': recette.banque.nom_banque if recette.banque else 'Non spécifiée'
                })
            
            # Ajouter quelques demandes de paiement pour le contexte WICKFLOW
            for demande in recent_demandes:
                activities.append({
                    'type': 'demande',
                    'description': f"Demande de paiement: {demande.description}",
                    'date': demande.date_demande.strftime('%d/%m/%Y %H:%M'),
                    'montant': float(demande.montant),
                    'statut': demande.statut
                })
            
            return sorted(activities, key=lambda x: x['date'], reverse=True)[:10]
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des activités récentes: {str(e)}", exc_info=True)
            return []


class HomeView(LoginRequiredMixin, TemplateView):
    """Page d'accueil pour les utilisateurs RBAC sans tableau de bord"""
    template_name = 'rapports/home_rbac.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Ajouter les informations sur l'utilisateur
        context['user_permissions'] = []
        context['user_modules'] = []
        
        # Vérifier les permissions et modules accessibles
        if hasattr(user, 'rbac_role') and user.rbac_role:
            # Modules accessibles selon les permissions
            if hasattr(user, 'can_access_module'):
                modules = ['banques', 'demandes', 'recettes', 'etats', 'clotures', 'releves']
                for module in modules:
                    if user.can_access_module(module):
                        context['user_modules'].append(module)
            
            # Permissions détaillées
            if hasattr(user, 'get_all_permissions'):
                context['user_permissions'] = user.get_all_permissions()
        
        return context


class RapportConsolideView(RoleRequiredMixin, TemplateView):
    """Vue pour les rapports consolidés"""
    template_name = 'rapports/rapport_consolide.html'
    permission_function = 'peut_voir_rapports'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter la logique pour les rapports consolidés ici
        return context
