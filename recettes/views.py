"""
Vues pour la gestion des recettes
"""
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Sum
from accounts.permissions import RoleRequiredMixin
from .models import Recette
from .forms import RecetteForm
from banques.models import CompteBancaire, Banque


class RecetteListView(RoleRequiredMixin, ListView):
    model = Recette
    template_name = 'recettes/recette_liste.html'
    context_object_name = 'recettes'
    paginate_by = 50
    permission_function = 'peut_voir_menu_recettes'
    
    def get_queryset(self):
        queryset = Recette.objects.select_related('banque', 'compte_bancaire', 'enregistre_par', 'valide_par')
        
        # Filtrage par année
        annee = self.request.GET.get('annee')
        if annee:
            try:
                queryset = queryset.filter(date_encaissement__year=int(annee))
            except ValueError:
                pass
        
        # Filtrage par mois
        mois = self.request.GET.get('mois')
        if mois:
            try:
                queryset = queryset.filter(date_encaissement__month=int(mois))
            except ValueError:
                pass
        
        # Filtrage par banque
        banque_id = self.request.GET.get('banque')
        if banque_id:
            queryset = queryset.filter(banque_id=banque_id)
        
        # Filtrage par statut de validation
        valide = self.request.GET.get('valide')
        if valide is not None:
            queryset = queryset.filter(valide=valide == 'true')
        
        return queryset.order_by('-date_encaissement', '-date_creation')
        
        # Filtrage par devise (montant > 0)
        devise = self.request.GET.get('devise')
        if devise == 'CDF':
            queryset = queryset.filter(montant_cdf__gt=0)
        elif devise == 'USD':
            queryset = queryset.filter(montant_usd__gt=0)
        
        # Recherche textuelle
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(reference__icontains=search) |
                Q(description__icontains=search) |
                Q(source_recette__icontains=search)
            )
        
        return queryset.order_by('-date_encaissement', '-date_creation')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculer les totaux
        queryset = self.get_queryset()
        context['total_usd'] = queryset.aggregate(total=Sum('montant_usd'))['total'] or 0
        context['total_cdf'] = queryset.aggregate(total=Sum('montant_cdf'))['total'] or 0
        
        # Liste des années disponibles
        context['annees'] = Recette.objects.values_list('date_encaissement__year', flat=True).distinct().order_by('-date_encaissement__year')
        
        # Liste des banques
        context['banques'] = Banque.objects.filter(active=True).order_by('nom_banque')
        
        # Paramètres de filtrage actuels
        context['filtres'] = {
            'annee': self.request.GET.get('annee', ''),
            'mois': self.request.GET.get('mois', ''),
            'banque': self.request.GET.get('banque', ''),
            'valide': self.request.GET.get('valide', ''),
            'devise': self.request.GET.get('devise', ''),
            'search': self.request.GET.get('search', ''),
        }
        
        return context


class RecetteCreateView(RoleRequiredMixin, CreateView):
    model = Recette
    form_class = RecetteForm
    template_name = 'recettes/recette_form.html'
    success_url = reverse_lazy('recettes:liste')
    permission_function = 'peut_saisir_demandes_recettes'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.enregistre_par = self.request.user
        # Auto-validation si c'est un comptable
        if self.request.user.is_comptable:
            form.instance.valide = True
            form.instance.valide_par = self.request.user
            form.instance.date_validation = timezone.now()
            messages.success(self.request, 'Recette enregistrée et validée avec succès.')
        else:
            messages.success(self.request, 'Recette enregistrée. En attente de validation.')
        
        return super().form_valid(form)


class RecetteUpdateView(LoginRequiredMixin, UpdateView):
    model = Recette
    form_class = RecetteForm
    template_name = 'recettes/recette_form.html'
    success_url = reverse_lazy('recettes:liste')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RecetteDetailView(LoginRequiredMixin, DetailView):
    model = Recette
    template_name = 'recettes/recette_detail.html'
    context_object_name = 'recette'


class RecetteValidationView(LoginRequiredMixin, DetailView):
    model = Recette
    template_name = 'recettes/recette_validation.html'
    context_object_name = 'recette'
    
    def dispatch(self, request, *args, **kwargs):
        self.recette = get_object_or_404(Recette, pk=kwargs['pk'])
        
        # Vérifier les permissions
        if not request.user.is_comptable:
            messages.error(request, 'Vous n\'avez pas la permission de valider cette recette.')
            return redirect('recettes:detail', pk=self.recette.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Validation de la recette {self.recette.reference}'
        return context
    
    def post(self, request, *args, **kwargs):
        recette = self.get_object()
        if not recette.valide:
            # Marquer la recette comme validée
            recette.valide = True
            recette.valide_par = request.user
            recette.date_validation = timezone.now()
            # Sauvegarder - cela déclenchera automatiquement la mise à jour du solde dans le modèle
            recette.save()
            messages.success(request, 'Recette validée avec succès! Le solde du compte bancaire a été mis à jour.')
        else:
            messages.info(request, 'Cette recette est déjà validée.')
        
        return redirect('recettes:detail', pk=recette.pk)


def load_comptes(request):
    """Vue AJAX pour charger les comptes bancaires selon la banque"""
    banque_id = request.GET.get('banque_id')
    if banque_id:
        comptes = CompteBancaire.objects.filter(banque_id=banque_id, actif=True)
        data = [{'id': c.id, 'intitule': str(c), 'devise': c.devise} for c in comptes]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

