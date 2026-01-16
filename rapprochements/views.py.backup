"""
Vues pour le rapprochement bancaire
"""
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import RapprochementBancaire
from .forms import RapprochementBancaireForm
from banques.models import CompteBancaire


class RapprochementBancaireListView(LoginRequiredMixin, ListView):
    model = RapprochementBancaire
    template_name = 'rapprochements/rapprochement_liste.html'
    context_object_name = 'rapprochements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = RapprochementBancaire.objects.select_related(
            'banque', 'compte_bancaire', 'releve_bancaire', 'observateur'
        )
        
        # Filtrage par banque
        banque_id = self.request.GET.get('banque')
        if banque_id:
            queryset = queryset.filter(banque_id=banque_id)
        
        # Filtrage par statut
        valide = self.request.GET.get('valide')
        if valide is not None:
            queryset = queryset.filter(valide=valide == 'true')
        
        # Filtrage par devise
        devise = self.request.GET.get('devise')
        if devise:
            queryset = queryset.filter(devise=devise)
        
        return queryset


class RapprochementBancaireCreateView(LoginRequiredMixin, CreateView):
    model = RapprochementBancaire
    form_class = RapprochementBancaireForm
    template_name = 'rapprochements/rapprochement_form.html'
    success_url = reverse_lazy('rapprochements:liste')
    
    def form_valid(self, form):
        form.instance.observateur = self.request.user
        messages.success(self.request, 'Rapprochement créé avec succès. Vous pouvez maintenant calculer le solde interne.')
        return super().form_valid(form)


class RapprochementBancaireUpdateView(LoginRequiredMixin, UpdateView):
    model = RapprochementBancaire
    form_class = RapprochementBancaireForm
    template_name = 'rapprochements/rapprochement_form.html'
    
    def get_success_url(self):
        return reverse_lazy('rapprochements:detail', kwargs={'pk': self.object.pk})


class RapprochementBancaireDetailView(LoginRequiredMixin, DetailView):
    model = RapprochementBancaire
    template_name = 'rapprochements/rapprochement_detail.html'
    context_object_name = 'rapprochement'


class RapprochementBancaireCalculerView(LoginRequiredMixin, DetailView):
    """Vue pour calculer automatiquement le solde interne"""
    model = RapprochementBancaire
    template_name = 'rapprochements/rapprochement_detail.html'
    
    def post(self, request, *args, **kwargs):
        rapprochement = self.get_object()
        
        try:
            rapprochement.calculer_solde_interne()
            messages.success(
                request, 
                f'Solde interne calculé: {rapprochement.solde_interne} {rapprochement.devise}. '
                f'Écart: {rapprochement.ecart} {rapprochement.devise}.'
            )
        except Exception as e:
            messages.error(request, f'Erreur lors du calcul: {str(e)}')
        
        return redirect('rapprochements:detail', pk=rapprochement.pk)


class RapprochementBancaireValidationView(LoginRequiredMixin, DetailView):
    """Vue pour valider un rapprochement (Auditeur uniquement)"""
    model = RapprochementBancaire
    template_name = 'rapprochements/rapprochement_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.rapprochement = get_object_or_404(RapprochementBancaire, pk=kwargs['pk'])
        
        # Vérifier les permissions
        if not request.user.peut_valider_rapprochement():
            messages.error(request, 'Vous n\'avez pas la permission de valider ce rapprochement.')
            return redirect('rapprochements:detail', pk=self.rapprochement.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        rapprochement = self.get_object()
        if not rapprochement.valide:
            rapprochement.valide = True
            rapprochement.save()
            
            messages.success(request, 'Rapprochement validé avec succès.')
        else:
            messages.warning(request, 'Ce rapprochement est déjà validé.')
        
        return redirect('rapprochements:detail', pk=rapprochement.pk)


def load_comptes(request):
    """Vue AJAX pour charger les comptes bancaires selon la banque"""
    banque_id = request.GET.get('banque_id')
    if banque_id:
        comptes = CompteBancaire.objects.filter(banque_id=banque_id, actif=True)
        data = [{'id': c.id, 'intitule': str(c), 'devise': c.devise} for c in comptes]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

