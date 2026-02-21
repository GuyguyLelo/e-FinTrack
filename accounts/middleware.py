"""
Middleware pour la gestion des accès selon les rôles
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


class AdminAccessMiddleware:
    """
    Middleware pour rediriger l'admin simple vers l'administration Django
    et bloquer l'accès aux interfaces utilisateur
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user = request.user
        
        if user.is_authenticated:
            # Redirection pour ADMIN : accès admin Django + natures économiques
            if user.role == 'ADMIN':
                # Rediriger vers les natures économiques par défaut
                if not (request.path.startswith('/admin/') or 
                        request.path.startswith('/demandes/natures/') or
                        request.path.startswith('/accounts/logout/') or
                        request.path.startswith('/static/') or
                        request.path.startswith('/media/')):
                    return redirect('/demandes/natures/')
            
            # Redirection pour DG et CD_FINANCE : uniquement tableau de bord feuille
            elif user.role in ['DG', 'CD_FINANCE']:
                allowed_urls = [
                    '/tableau-bord-feuilles/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Vérifier si l'URL est autorisée
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/tableau-bord-feuilles/')
            
            # Redirection pour OPERATEUR_SAISIE : accès recettes/dépenses/états (pas tableau de bord)
            elif user.role == 'OPERATEUR_SAISIE':
                allowed_urls = [
                    '/recettes/feuille/',
                    '/demandes/depenses/feuille/',
                    '/tableau-bord-feuilles/etats-depenses/',
                    '/tableau-bord-feuilles/etats-recettes/',
                    '/tableau-bord-feuilles/rapport-selection/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Si l'URL n'est pas autorisée, rediriger vers les recettes
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/recettes/feuille/')
            
            # Bloquer l'accès au tableau de bord pour les rôles non autorisés
            elif request.path == '/' and not (user.peut_voir_tableau_bord() or user.peut_ajouter_nature_economique()):
                # Rediriger vers une page appropriée selon le rôle
                if user.role == 'ADMIN':
                    return redirect('/demandes/natures/')  # Rediriger vers les natures économiques
                elif user.role == 'OPERATEUR_SAISIE':
                    return redirect('/demandes/')  # Rediriger vers les demandes
                elif user.role == 'AGENT_PAYEUR':
                    return redirect('/demandes/paiements/')  # Rediriger vers les paiements
                else:
                    # Pour les autres rôles, rediriger vers l'admin Django s'ils y ont accès
                    if user.peut_acceder_admin_django():
                        return redirect('/admin/')
                    else:
                        return redirect('/accounts/login/')
        
        response = self.get_response(request)
        return response
