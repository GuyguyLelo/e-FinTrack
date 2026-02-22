from django.urls import path
from . import views

app_name = 'clotures'

urlpatterns = [
    path('', views.ClotureListView.as_view(), name='cloture_list'),
    path('<int:pk>/', views.ClotureDetailView.as_view(), name='cloture_detail'),
    path('<int:pk>/cloturer/', views.cloture_periode, name='cloture_periode'),
    path('<int:pk>/calculer-soldes/', views.calculer_soldes, name='calculer_soldes'),
    path('periode-actuelle/', views.periode_actuelle, name='periode_actuelle'),
]
