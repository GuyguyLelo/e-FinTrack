"""
Middleware pour la gestion des accès selon les rôles (RBAC en dur)
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


class AdminAccessMiddleware:
    """
    Middleware pour rediriger selon les rôles avec conditions en dur
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user = request.user
        
        if user.is_authenticated:
            # USERS DE DAF
            if user.role == 'OpsDaf':
                # Opérateur de saisie du DAF : accès aux dépenses/recettes/états feuilles
                allowed_urls = [
                    '/demandes/depenses/feuille/',
                    '/recettes/feuille/',
                    '/tableau-bord-feuilles/etats-',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/demandes/depenses/feuille/')
            
            elif user.role in ['DirDaf', 'DivDaf']:
                # Direction DAF : accès au tableau de bord feuilles et clôtures
                allowed_urls = [
                    '/tableau-bord-feuilles/',
                    '/clotures/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/tableau-bord-feuilles/')
            
            elif user.role == 'AdminDaf':
                # Administration DAF : accès aux natures et services
                allowed_urls = [
                    '/demandes/natures/',
                    '/accounts/services/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/demandes/natures/')
            
            # USERS NORMALS (WICKFLOW)
            elif user.role == 'ADMIN':
                # Administrateur : tout voir sans modification
                allowed_urls = [
                    '/demandes/',
                    '/recettes/',
                    '/accounts/users/',
                    '/accounts/services/',
                    '/demandes/natures/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/demandes/')
            
            elif user.role == 'DG':
                # Directeur Général : voir tableau bord, demandes, paiements, valider demandes
                allowed_urls = [
                    '/',  # Tableau de bord WICKFLOW (racine)
                    '/demandes/',
                    '/recettes/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Éviter la boucle de redirection : ne pas rediriger si déjà sur /
                if not any(request.path.startswith(url) for url in allowed_urls) and request.path != '/':
                    return redirect('/')
            
            elif user.role == 'DF':
                # Directeur Financier : tout voir sans modification
                allowed_urls = [
                    '/',  # Tableau de bord WICKFLOW (racine)
                    '/demandes/',
                    '/recettes/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Éviter la boucle de redirection : ne pas rediriger si déjà sur /
                if not any(request.path.startswith(url) for url in allowed_urls) and request.path != '/':
                    return redirect('/')
            
            elif user.role == 'CD_FINANCE':
                # Chef Division Finance : tout voir, créer relevés, consulter dépenses, créer états
                allowed_urls = [
                    '/',  # Tableau de bord WICKFLOW (racine)
                    '/demandes/',
                    '/recettes/',
                    '/releves/creer/',
                    '/tableau-bord-feuilles/etats-',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                # Éviter la boucle de redirection : ne pas rediriger si déjà sur /
                if not any(request.path.startswith(url) for url in allowed_urls) and request.path != '/':
                    return redirect('/')
            
            elif user.role == 'OPERATEUR_SAISIE':
                # Opérateur de Saisie : saisir demandes et recettes (pas tableau bord)
                allowed_urls = [
                    '/demandes/depenses/feuille/',
                    '/recettes/feuille/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/demandes/depenses/feuille/')
            
            elif user.role == 'AGENT_PAYEUR':
                # Agent Payeur : effectuer les paiements
                allowed_urls = [
                    '/demandes/paiements/',
                    '/accounts/logout/',
                    '/static/',
                    '/media/',
                ]
                
                if not any(request.path.startswith(url) for url in allowed_urls):
                    return redirect('/demandes/paiements/')
            
            # SuperAdmin : accès complet
            elif user.is_superuser:
                # Le SuperAdmin peut accéder à tout
                pass
            
            # Bloquer l'accès au tableau-bord-feuille pour les non-DAF
            if request.path.startswith('/tableau-bord-feuilles/') and user.role not in ['OpsDaf', 'DirDaf', 'DivDaf', 'AdminDaf', 'SUPER_ADMIN']:
                if user.is_superuser:
                    pass  # SuperAdmin a accès
                else:
                    # Rediriger vers le tableau de bord approprié
                    if user.role in ['DG', 'DF', 'CD_FINANCE']:
                        # Éviter la boucle de redirection : ne pas rediriger si déjà sur /
                        if request.path != '/':
                            return redirect('/')
                    elif user.role == 'ADMIN':
                        return redirect('/demandes/')
                    elif user.role == 'OPERATEUR_SAISIE':
                        return redirect('/demandes/depenses/feuille/')
                    elif user.role == 'AGENT_PAYEUR':
                        return redirect('/demandes/paiements/')
                    else:
                        return redirect('/accounts/login/')
        
        response = self.get_response(request)
        return response
