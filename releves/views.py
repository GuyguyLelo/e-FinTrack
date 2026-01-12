"""
Vues pour la gestion des relevés bancaires
"""
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import ReleveBancaire, MouvementBancaire
from .forms import ReleveBancaireForm, MouvementBancaireForm
from banques.models import CompteBancaire


class ReleveBancaireListView(LoginRequiredMixin, ListView):
    model = ReleveBancaire
    template_name = 'releves/releve_liste.html'
    context_object_name = 'releves'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ReleveBancaire.objects.select_related(
            'banque', 'compte_bancaire', 'saisi_par', 'valide_par'
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


class ReleveBancaireCreateView(LoginRequiredMixin, CreateView):
    model = ReleveBancaire
    form_class = ReleveBancaireForm
    template_name = 'releves/releve_form.html'
    success_url = reverse_lazy('releves:liste')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.saisi_par = self.request.user
        messages.success(self.request, 'Relevé bancaire créé avec succès. Vous pouvez maintenant ajouter les mouvements.')
        return super().form_valid(form)


class ReleveBancaireUpdateView(LoginRequiredMixin, UpdateView):
    model = ReleveBancaire
    form_class = ReleveBancaireForm
    template_name = 'releves/releve_form.html'
    
    def get_success_url(self):
        return reverse_lazy('releves:detail', kwargs={'pk': self.object.pk})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ReleveBancaireDetailView(LoginRequiredMixin, DetailView):
    model = ReleveBancaire
    template_name = 'releves/releve_detail.html'
    context_object_name = 'releve'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mouvements'] = self.object.mouvements.all()
        return context


class ReleveBancaireValidationView(LoginRequiredMixin, DetailView):
    model = ReleveBancaire
    template_name = 'releves/releve_validation.html'
    context_object_name = 'releve'
    
    def dispatch(self, request, *args, **kwargs):
        self.releve = get_object_or_404(ReleveBancaire, pk=kwargs['pk'])
        
        # Vérifier les permissions
        if not request.user.peut_valider_releve():
            messages.error(request, 'Vous n\'avez pas la permission de valider ce relevé.')
            return redirect('releves:detail', pk=self.releve.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        releve = self.get_object()
        if not releve.valide:
            releve.valide = True
            releve.valide_par = request.user
            releve.date_validation = timezone.now()
            releve.save()
            
            messages.success(request, 'Relevé bancaire validé avec succès.')
        else:
            messages.warning(request, 'Ce relevé est déjà validé.')
        
        return redirect('releves:detail', pk=releve.pk)


class MouvementBancaireCreateView(LoginRequiredMixin, CreateView):
    model = MouvementBancaire
    form_class = MouvementBancaireForm
    template_name = 'releves/mouvement_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.releve = get_object_or_404(ReleveBancaire, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['releve'] = self.releve
        return context
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['releve'] = self.releve
        return kwargs
    
    def form_valid(self, form):
        form.instance.releve = self.releve
        messages.success(self.request, 'Mouvement bancaire ajouté avec succès.')
        return redirect('releves:detail', pk=self.releve.pk)


class MouvementBancaireDeleteView(LoginRequiredMixin, DeleteView):
    model = MouvementBancaire
    
    def get_success_url(self):
        return reverse_lazy('releves:detail', kwargs={'pk': self.object.releve.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Mouvement bancaire supprimé avec succès.')
        return super().delete(request, *args, **kwargs)


def load_comptes(request):
    """Vue AJAX pour charger les comptes bancaires selon la banque"""
    banque_id = request.GET.get('banque_id')
    if banque_id:
        comptes = CompteBancaire.objects.filter(banque_id=banque_id, actif=True)
        data = [{'id': c.id, 'intitule': str(c), 'devise': c.devise} for c in comptes]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

