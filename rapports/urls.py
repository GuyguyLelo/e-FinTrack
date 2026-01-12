"""
URLs pour les rapports
"""
from django.urls import path
from . import views

app_name = 'rapports'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('consolide/', views.RapportConsolideView.as_view(), name='consolide'),
]

