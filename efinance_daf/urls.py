"""
URL configuration for efinance_daf project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('rapports.urls')),  # Dashboard à la racine
    path('accounts/', include('accounts.urls')),
    path('banques/', include('banques.urls')),
    path('demandes/', include('demandes.urls')),
    path('recettes/', include('recettes.urls')),
    path('releves/', include('releves.urls')),
    path('etats/', include('etats.urls')),
    path('tableau-bord-feuilles/', include('tableau_bord_feuilles.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

