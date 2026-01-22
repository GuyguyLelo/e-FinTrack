"""
Vues pour la gestion des banques et comptes bancaires
"""
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from .models import Banque, CompteBancaire
from .forms import BanqueForm, CompteBancaireForm


class BanqueListView(LoginRequiredMixin, ListView):
    model = Banque
    template_name = 'banques/banque_liste.html'
    context_object_name = 'banques'
    paginate_by = 20


class BanqueCreateView(LoginRequiredMixin, CreateView):
    model = Banque
    form_class = BanqueForm
    template_name = 'banques/banque_form.html'
    success_url = reverse_lazy('banques:liste')


class BanqueUpdateView(LoginRequiredMixin, UpdateView):
    model = Banque
    form_class = BanqueForm
    template_name = 'banques/banque_form.html'
    success_url = reverse_lazy('banques:liste')


class BanqueDetailView(LoginRequiredMixin, DetailView):
    model = Banque
    template_name = 'banques/banque_detail.html'
    context_object_name = 'banque'


class CompteBancaireListView(LoginRequiredMixin, ListView):
    model = CompteBancaire
    template_name = 'banques/compte_liste.html'
    context_object_name = 'comptes'
    paginate_by = 20


class CompteBancaireCreateView(LoginRequiredMixin, CreateView):
    model = CompteBancaire
    form_class = CompteBancaireForm
    template_name = 'banques/compte_form.html'
    success_url = reverse_lazy('banques:comptes_liste')


class CompteBancaireUpdateView(LoginRequiredMixin, UpdateView):
    model = CompteBancaire
    form_class = CompteBancaireForm
    template_name = 'banques/compte_form.html'
    success_url = reverse_lazy('banques:comptes_liste')
    
    def form_valid(self, form):
        """Gérer la validation du formulaire lors de la modification"""
        # Sauvegarder le formulaire (cela met à jour l'objet)
        response = super().form_valid(form)
        
        # Si le solde_initial a changé et que le solde_courant n'a jamais été modifié manuellement,
        # on peut optionnellement mettre à jour le solde_courant
        # Mais ici, on garde le solde_courant tel quel car il peut avoir été modifié par des opérations
        
        return response


class CompteBancaireDetailView(LoginRequiredMixin, DetailView):
    model = CompteBancaire
    template_name = 'banques/compte_detail.html'
    context_object_name = 'compte'

