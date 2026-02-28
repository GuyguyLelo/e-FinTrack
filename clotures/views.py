from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.utils import timezone
from django.db import transaction
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import ClotureMensuelle
from .forms import ClotureMensuelleForm
from demandes.models import DepenseFeuille
from recettes.models import RecetteFeuille


class ClotureRequiredMixin(UserPassesTestMixin):
    """Mixin pour vérifier que l'utilisateur peut clôturer"""
    def test_func(self):
        return self.request.user.role in ['DG', 'CD_FINANCE']


class ClotureListView(LoginRequiredMixin, ListView):
    """Liste des clôtures mensuelles"""
    model = ClotureMensuelle
    template_name = 'clotures/cloture_list.html'
    context_object_name = 'clotures'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrer par année si spécifié
        annee = self.request.GET.get('annee')
        if annee:
            queryset = queryset.filter(annee=annee)
        return queryset.order_by('-annee', '-mois')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['annees_disponibles'] = ClotureMensuelle.objects.values_list(
            'annee', flat=True
        ).distinct().order_by('-annee')
        context['annee_selectionnee'] = self.request.GET.get('annee')
        context['peut_cloturer'] = self.request.user.role in ['DG', 'CD_FINANCE']
        return context


class ClotureDetailView(LoginRequiredMixin, DetailView, FormMixin):
    """Détail d'une clôture mensuelle"""
    model = ClotureMensuelle
    template_name = 'clotures/cloture_detail.html'
    context_object_name = 'cloture'
    form_class = ClotureMensuelleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cloture = self.get_object()
        
        # Récupérer les dépenses et recettes de la période
        context['depenses'] = DepenseFeuille.objects.filter(
            mois=cloture.mois,
            annee=cloture.annee
        ).order_by('-date')
        
        context['recettes'] = RecetteFeuille.objects.filter(
            mois=cloture.mois,
            annee=cloture.annee
        ).order_by('-date')
        
        context['peut_cloturer'] = self.request.user.role in ['DG', 'CD_FINANCE']
        context['periode_modifiable'] = cloture.peut_etre_modifie()
        
        return context

    def post(self, request, *args, **kwargs):
        cloture = self.get_object()
        
        if not cloture.peut_etre_modifie():
            messages.error(request, "Cette période est déjà clôturée et ne peut plus être modifiée.")
            return redirect('clotures:cloture_detail', pk=cloture.pk)
        
        if request.user.role not in ['DG', 'CD_FINANCE']:
            messages.error(request, "Vous n'avez pas les droits pour clôturer une période.")
            return redirect('clotures:cloture_detail', pk=cloture.pk)
        
        # Vérifier si la période peut être clôturée
        peut_cloturer, message = cloture.peut_etre_cloture()
        if not peut_cloturer:
            messages.error(request, message)
            return redirect('clotures:cloture_detail', pk=cloture.pk)
        
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        cloture = self.get_object()
        observations = form.cleaned_data.get('observations', '')
        
        try:
            cloture.cloturer(self.request.user, observations)
            messages.success(
                self.request, 
                f"La période {cloture.mois:02d}/{cloture.annee} a été clôturée avec succès."
            )
        except Exception as e:
            messages.error(self.request, f"Erreur lors de la clôture : {str(e)}")
        
        return redirect('clotures:cloture_detail', pk=cloture.pk)


@login_required
def cloture_periode(request, pk):
    """Vue pour clôturer une période"""
    cloture = get_object_or_404(ClotureMensuelle, pk=pk)
    
    if request.user.role not in ['DG', 'CD_FINANCE']:
        messages.error(request, "Vous n'avez pas les droits pour clôturer une période.")
        return redirect('clotures:cloture_detail', pk=cloture.pk)
    
    if not cloture.peut_etre_modifie():
        messages.error(request, "Cette période est déjà clôturée.")
        return redirect('clotures:cloture_detail', pk=cloture.pk)
    
    # Vérifier si la période peut être clôturée
    peut_cloturer, message = cloture.peut_etre_cloture()
    if not peut_cloturer:
        messages.error(request, message)
        return redirect('clotures:cloture_detail', pk=cloture.pk)
    
    if request.method == 'POST':
        form = ClotureMensuelleForm(request.POST)
        if form.is_valid():
            observations = form.cleaned_data.get('observations', '')
            try:
                cloture.cloturer(request.user, observations)
                messages.success(
                    request, 
                    f"La période {cloture.mois:02d}/{cloture.annee} a été clôturée avec succès."
                )
            except Exception as e:
                messages.error(request, f"Erreur lors de la clôture : {str(e)}")
            
            return redirect('clotures:cloture_detail', pk=cloture.pk)
    else:
        form = ClotureMensuelleForm()
    
    return render(request, 'clotures/cloture_confirm.html', {
        'cloture': cloture,
        'form': form
    })


@login_required
def calculer_soldes(request, pk):
    """Vue pour recalculer les soldes d'une période"""
    cloture = get_object_or_404(ClotureMensuelle, pk=pk)
    
    if not cloture.peut_etre_modifie():
        return JsonResponse({
            'error': 'Cette période est déjà clôturée'
        }, status=400)
    
    try:
        cloture.calculer_soldes()
        return JsonResponse({
            'success': True,
            'total_recettes_fc': str(cloture.total_recettes_fc),
            'total_recettes_usd': str(cloture.total_recettes_usd),
            'total_depenses_fc': str(cloture.total_depenses_fc),
            'total_depenses_usd': str(cloture.total_depenses_usd),
            'solde_net_fc': str(cloture.solde_net_fc),
            'solde_net_usd': str(cloture.solde_net_usd)
        })
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@login_required
def periode_actuelle(request):
    """Vue pour afficher la période actuelle"""
    cloture = ClotureMensuelle.get_periode_actuelle()
    
    # Récupérer les dépenses et recettes de la période actuelle
    depenses = DepenseFeuille.objects.filter(
        mois=cloture.mois,
        annee=cloture.annee
    ).order_by('-date')
    
    recettes = RecetteFeuille.objects.filter(
        mois=cloture.mois,
        annee=cloture.annee
    ).order_by('-date')
    
    return render(request, 'clotures/periode_actuelle.html', {
        'cloture': cloture,
        'depenses': depenses,
        'recettes': recettes,
        'peut_cloturer': request.user.role in ['DG', 'CD_FINANCE'],
        'periode_modifiable': cloture.peut_etre_modifie()
    })
