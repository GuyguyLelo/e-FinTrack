"""
Middleware personnalisé pour gérer les exceptions de session
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)

# Importer l'exception SessionInterrupted de Django 5.0+
try:
    from django.contrib.sessions.exceptions import SessionInterrupted
except ImportError:
    # Si l'exception n'existe pas (Django < 5.0), créer une classe factice
    SessionInterrupted = type('SessionInterrupted', (Exception,), {})


class SessionInterruptedMiddleware:
    """
    Middleware pour gérer gracieusement l'exception SessionInterrupted
    qui peut survenir dans Django 5.0+ lorsque la session est supprimée
    pendant qu'une requête est en cours.
    
    Ce middleware doit être placé APRÈS SessionMiddleware dans MIDDLEWARE.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Vérifier si c'est une erreur de session interrompue
            if self._is_session_error(e):
                return self._handle_session_error(request, e)
            # Si ce n'est pas une erreur de session, laisser Django la gérer
            raise
    
    def process_exception(self, request, exception):
        """
        Cette méthode est appelée lorsqu'une exception est levée dans la chaîne de middleware
        ou dans une vue. Elle est appelée pour TOUS les middlewares après celui qui a causé l'exception.
        """
        if self._is_session_error(exception):
            return self._handle_session_error(request, exception)
        return None  # Laisser les autres middlewares gérer l'exception
    
    def _is_session_error(self, exception):
        """Vérifie si l'exception est liée à une session interrompue"""
        return (
            isinstance(exception, SessionInterrupted) or
            'SessionInterrupted' in type(exception).__name__ or
            ('session' in str(exception).lower() and 'deleted' in str(exception).lower()) or
            'SessionInterrupted' in str(exception) or
            'session was deleted' in str(exception).lower()
        )
    
    def _handle_session_error(self, request, exception):
        """Gère l'erreur de session en nettoyant et redirigeant"""
        username = 'anonyme'
        try:
            if hasattr(request, 'user') and hasattr(request.user, 'username'):
                username = getattr(request.user, 'username', 'anonyme')
        except Exception:
            pass
        
        logger.warning(f"Session interrompue pour l'utilisateur: {username}")
        
        # Tenter de nettoyer la session
        try:
            if hasattr(request, 'session'):
                request.session.flush()
        except Exception as cleanup_error:
            logger.debug(f"Erreur lors du nettoyage de session: {cleanup_error}")
        
        try:
            if hasattr(request, 'user') and hasattr(request.user, 'is_authenticated'):
                if request.user.is_authenticated:
                    logout(request)
        except Exception as logout_error:
            logger.debug(f"Erreur lors de la déconnexion: {logout_error}")
        
        # Rediriger vers la page de login avec un message
        try:
            login_url = reverse('accounts:login')
            return HttpResponseRedirect(f"{login_url}?session_expired=1")
        except Exception:
            # En cas d'erreur lors de la redirection, retourner une réponse simple
            return HttpResponseRedirect('/accounts/login/?session_expired=1')
