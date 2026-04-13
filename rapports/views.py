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
                        from django.shortcuts import redirect
                        return redirect('/home/')
            
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
        """Obtenir les statistiques générales"""
        try:
            # Statistiques des banques
            banques_count = Banque.objects.count()
            comptes_count = CompteBancaire.objects.count()
            
            # Statistiques des dépenses
            depenses_count = Depense.objects.filter(
                date_creation__range=(start_date, end_date)
            ).count()
            
            depenses_total = Depense.objects.filter(
                date_creation__range=(start_date, end_date)
            ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
            
            # Statistiques des recettes
            recettes_count = Recette.objects.filter(
                date_creation__range=(start_date, end_date)
            ).count()
            
            recettes_total = Recette.objects.filter(
                date_creation__range=(start_date, end_date)
            ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
            
            # Statistiques des demandes
            demandes_count = DemandePaiement.objects.filter(
                date_creation__range=(start_date, end_date)
            ).count()
            
            demandes_total = DemandePaiement.objects.filter(
                date_creation__range=(start_date, end_date)
            ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
            
            return {
                'banques_count': banques_count,
                'comptes_count': comptes_count,
                'depenses_count': depenses_count,
                'depenses_total': depenses_total,
                'recettes_count': recettes_count,
                'recettes_total': recettes_total,
                'demandes_count': demandes_count,
                'demandes_total': demandes_total,
                'solde_net': recettes_total - depenses_total,
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques générales: {str(e)}", exc_info=True)
            return {}
    
    def get_chart_data(self, start_date, end_date):
        """Préparer les données pour les graphiques"""
        try:
            # Données mensuelles pour les 6 derniers mois
            chart_data = []
            for i in range(6):
                month_start = (start_date - timedelta(days=30*i)).replace(day=1)
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                month_depenses = Depense.objects.filter(
                    date_creation__range=(month_start, month_end)
                ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
                
                month_recettes = Recette.objects.filter(
                    date_creation__range=(month_start, month_end)
                ).aggregate(total=Sum('montant'))['total'] or Decimal('0')
                
                chart_data.append({
                    'month': month_start.strftime('%b %Y'),
                    'depenses': float(month_depenses),
                    'recettes': float(month_recettes),
                    'solde': float(month_recettes - month_depenses)
                })
            
            return {
                'chart_data': list(reversed(chart_data)),
                'chart_labels': [item['month'] for item in chart_data]
            }
        except Exception as e:
            logger.error(f"Erreur lors de la préparation des données de graphique: {str(e)}", exc_info=True)
            return {'chart_data': [], 'chart_labels': []}
    
    def get_recent_activities(self):
        """Obtenir les dernières activités"""
        try:
            activities = []
            
            # Dernières dépenses
            recent_depenses = Depense.objects.order_by('-date_creation')[:5]
            for depense in recent_depenses:
                activities.append({
                    'type': 'depense',
                    'description': f"Dépense: {depense.description[:50]}",
                    'amount': depense.montant,
                    'date': depense.date_creation,
                    'icon': 'bi-cash-stack',
                    'color': 'danger'
                })
            
            # Dernières recettes
            recent_recettes = Recette.objects.order_by('-date_creation')[:5]
            for recette in recent_recettes:
                activities.append({
                    'type': 'recette',
                    'description': f"Recette: {recette.description[:50]}",
                    'amount': recette.montant,
                    'date': recette.date_creation,
                    'icon': 'bi-cash',
                    'color': 'success'
                })
            
            # Dernières demandes
            recent_demandes = DemandePaiement.objects.order_by('-date_creation')[:5]
            for demande in recent_demandes:
                activities.append({
                    'type': 'demande',
                    'description': f"Demande: {demande.description[:50]}",
                    'amount': demande.montant,
                    'date': demande.date_creation,
                    'icon': 'bi-file-earmark-text',
                    'color': 'info'
                })
            
            # Trier par date
            activities.sort(key=lambda x: x['date'], reverse=True)
            
            return activities[:10]  # Limiter à 10 activités
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
