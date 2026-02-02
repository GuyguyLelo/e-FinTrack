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
        
        # Si l'utilisateur est authentifié
        if user.is_authenticated:
            # Redirection pour l'admin simple
            if user.role == 'ADMIN':
                allowed_urls = [
                    '/admin/',
                    '/admin/login/',
                    '/admin/logout/',
                    '/accounts/logout/',
                ]
                
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/admin/')
            
            # Bloquer l'accès au tableau de bord pour les rôles non autorisés
            elif request.path == '/' and not user.peut_voir_tableau_bord():
                # Rediriger vers une page appropriée selon le rôle
                if user.role == 'OPERATEUR_SAISIE':
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
