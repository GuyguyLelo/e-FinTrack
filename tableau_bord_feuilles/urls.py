from django.urls import path
from . import views

app_name = 'tableau_bord_feuilles'

urlpatterns = [
    path('', views.tableau_bord_feuilles, name='tableau_bord_feuilles'),
    path('operations/', views.detail_operations, name='detail_operations'),
]
