"""
Vues pour la gestion des banques et comptes bancaires
"""
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from accounts.permissions import RoleRequiredMixin
from .models import Banque, CompteBancaire
from .forms import BanqueForm, CompteBancaireForm


class BanqueListView(RoleRequiredMixin, ListView):
    model = Banque
    template_name = 'banques/banque_liste.html'
    context_object_name = 'banques'
    paginate_by = 20
    required_roles = ['SUPER_ADMIN']


class BanqueCreateView(RoleRequiredMixin, CreateView):
    model = Banque
    form_class = BanqueForm
    template_name = 'banques/banque_form.html'
    success_url = reverse_lazy('banques:liste')
    required_roles = ['SUPER_ADMIN']


class BanqueUpdateView(RoleRequiredMixin, UpdateView):
    model = Banque
    form_class = BanqueForm
    template_name = 'banques/banque_form.html'
    success_url = reverse_lazy('banques:liste')
    required_roles = ['SUPER_ADMIN']


class BanqueDetailView(RoleRequiredMixin, DetailView):
    model = Banque
    template_name = 'banques/banque_detail.html'
    context_object_name = 'banque'
    required_roles = ['SUPER_ADMIN']


class CompteBancaireListView(RoleRequiredMixin, ListView):
    model = CompteBancaire
    template_name = 'banques/compte_liste.html'
    context_object_name = 'comptes'
    paginate_by = 20
    required_roles = ['SUPER_ADMIN']


class CompteBancaireCreateView(RoleRequiredMixin, CreateView):
    model = CompteBancaire
    form_class = CompteBancaireForm
    template_name = 'banques/compte_form.html'
    success_url = reverse_lazy('banques:comptes_liste')
    required_roles = ['SUPER_ADMIN']


class CompteBancaireUpdateView(RoleRequiredMixin, UpdateView):
    model = CompteBancaire
    form_class = CompteBancaireForm
    template_name = 'banques/compte_form.html'
    success_url = reverse_lazy('banques:comptes_liste')
    required_roles = ['SUPER_ADMIN']

    def form_valid(self, form):
        """Gérer la validation du formulaire lors de la modification"""
        # Sauvegarder le formulaire (cela met à jour l'objet)
        response = super().form_valid(form)
        
        # Si le solde_initial a changé et que le solde_courant n'a jamais été modifié manuellement,
        # on peut optionnellement mettre à jour le solde_courant
        # Mais ici, on garde le solde_courant tel quel car il peut avoir été modifié par des opérations
        
        return response


class CompteBancaireDetailView(RoleRequiredMixin, DetailView):
    model = CompteBancaire
    template_name = 'banques/compte_detail.html'
    context_object_name = 'compte'
    required_roles = ['SUPER_ADMIN']
