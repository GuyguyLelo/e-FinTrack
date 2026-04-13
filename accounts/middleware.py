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
            # PRIORITÉ AU SYSTÈME RBAC
            # Si l'utilisateur a un rôle RBAC, ignorer le middleware legacy
            if hasattr(user, 'rbac_role_modele') and user.rbac_role_modele:
                # Laisser passer les utilisateurs RBAC - gérés par la vue de connexion
                return self.get_response(request)
            
            # Redirection prioritaire pour les admins vers les natures économiques
            if user.role == 'ADMIN' and request.path == '/':
                return redirect('/demandes/natures/')  # Redirection immédiate pour les admins
        
        if user.is_authenticated:
            # Redirection pour ADMIN : accès admin Django + natures économiques + services
            if user.role == 'ADMIN':
                # Rediriger les admins directement vers les natures économiques
                if request.path == '/':
                    return redirect('/demandes/natures/')  # Page par défaut pour les admins
                # Laisser l'admin naviguer librement sur les autres pages
                pass
            
            # Redirection pour DG et CD_FINANCE : PAS d'accès au tableau-bord-feuilles (seulement WICKFLOW)
            elif user.role in ['DG', 'CD_FINANCE']:
                allowed_urls = [
                    '/demandes/',
                    '/recettes/',
                    '/paiements/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Vérifier si l'URL est autorisée
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/demandes/')
            
            # Redirection pour OPERATEUR_SAISIE : accès recettes/dépenses/états (pas tableau de bord)
            elif user.role == 'OPERATEUR_SAISIE':
                allowed_urls = [
                    '/recettes/feuille/',
                    '/demandes/depenses/feuille/',
                    '/tableau-bord-feuilles/etats-depenses/',
                    '/tableau-bord-feuilles/etats-recettes/',
                    '/tableau-bord-feuilles/rapports/',
                    '/tableau-bord-feuilles/api/',
                    '/tableau-bord-feuilles/preview-etats/',
                    '/tableau-bord-feuilles/generer-etats/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Si l'URL n'est pas autorisée et n'est pas déjà une redirection, rediriger vers les recettes
                if not any(request.path.startswith(url) for url in allowed_urls):
                    # Éviter la boucle de redirection
                    if request.path not in ['/recettes/feuille/', '/']:
                        return redirect('/recettes/feuille/')
            
            # Redirection pour les rôles DAF : accès au tableau-bord-feuilles
            elif user.role in ['OpsDaf', 'DirDaf', 'DivDaf', 'AdminDaf']:
                allowed_urls = [
                    '/tableau-bord-feuilles/',
                    '/clotures/',
                    '/demandes/natures/',
                    '/accounts/services/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Pour OpsDaf, autoriser aussi les dépenses/recettes feuilles
                if user.role == 'OpsDaf':
                    allowed_urls.extend([
                        '/demandes/depenses/feuille/',
                        '/recettes/feuille/',
                        '/tableau-bord-feuilles/etats-depenses/',
                        '/tableau-bord-feuilles/etats-recettes/',
                    ])
                
                # Si l'URL n'est pas autorisée, rediriger vers le tableau de bord DAF
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/tableau-bord-feuilles/')
            
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
            # Pour les admins, permettre l'accès libre aux pages autorisées
            elif user.role == 'ADMIN' and request.path.startswith('/tableau-bord-feuilles/'):
                # Les admins peuvent voir le tableau de bord même sans permission spéciale
                # Ne pas rediriger - laisser passer
                pass
        
        response = self.get_response(request)
        return response
