from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count, Avg, Q, F, DecimalField
from django.db.models.functions import ExtractYear, ExtractMonth, TruncMonth
from django.utils.timezone import now
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib.humanize.templatetags.humanize import intcomma
from demandes.models import DepenseFeuille
from recettes.models import RecetteFeuille
from banques.models import Banque
import json


def format_montant(montant):
    """Formater un montant avec séparateurs de milliers"""
    if montant:
        return f"{intcomma(montant)}"
    return "0"

def format_montant_decimal(montant):
    """Formater un montant décimal avec séparateurs de milliers"""
    if montant:
        return f"{intcomma(montant)}"
    return "0,00"


def tableau_bord_feuilles(request):
    """
    Tableau de bord dédié aux données des feuilles DEPENSES et RECETTES
    """
    today = now()
    current_year = today.year
    current_month = today.month
    
    # Récupérer les données des dépenses (feuille)
    depenses = DepenseFeuille.objects.all()
    recettes = RecetteFeuille.objects.all()
    
    # Récupérer la dernière année disponible avec données significatives
    derniere_annee_depense = DepenseFeuille.objects.order_by('-annee').first()
    derniere_annee_recette = RecetteFeuille.objects.order_by('-annee').first()
    
    # Chercher l'année la plus récente avec des données USD non nulles
    annee_avec_usd_depense = DepenseFeuille.objects.filter(montant_usd__gt=0).order_by('-annee').first()
    annee_avec_usd_recette = RecetteFeuille.objects.filter(montant_usd__gt=0).order_by('-annee').first()
    
    if annee_avec_usd_depense and annee_avec_usd_recette:
        default_year = max(annee_avec_usd_depense.annee, annee_avec_usd_recette.annee)
    elif annee_avec_usd_depense:
        default_year = annee_avec_usd_depense.annee
    elif annee_avec_usd_recette:
        default_year = annee_avec_usd_recette.annee
    elif derniere_annee_depense and derniere_annee_recette:
        default_year = max(derniere_annee_depense.annee, derniere_annee_recette.annee)
    elif derniere_annee_depense:
        default_year = derniere_annee_depense.annee
    elif derniere_annee_recette:
        default_year = derniere_annee_recette.annee
    else:
        default_year = current_year
    
    # Filtres par année et mois (valeurs par défaut : TOUTES les données sans filtre)
    annee_filter = request.GET.get('annee')
    mois_filter = request.GET.get('mois')
    banque_filter = request.GET.get('banque')
    
    # Par défaut, ne filtrer par rien pour afficher TOUTES les données
    # Seulement appliquer les filtres si l'utilisateur les sélectionne explicitement
    if annee_filter:
        annee_filter = int(annee_filter)
        depenses = depenses.filter(annee=annee_filter)
        recettes = recettes.filter(annee=annee_filter)
    
    if mois_filter:
        mois_filter = int(mois_filter)
        depenses = depenses.filter(mois=mois_filter)
        recettes = recettes.filter(mois=mois_filter)
        
    if banque_filter:
        depenses = depenses.filter(banque_id=banque_filter)
        recettes = recettes.filter(banque_id=banque_filter)
    
    # Statistiques générales
    total_depenses_cdf = depenses.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
    total_depenses_usd = depenses.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
    total_recettes_cdf = recettes.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
    total_recettes_usd = recettes.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
    
    # Soldes
    solde_cdf = total_recettes_cdf - total_depenses_cdf
    solde_usd = total_recettes_usd - total_depenses_usd
    
    # Nombre d'opérations
    nb_depenses = depenses.count()
    nb_recettes = recettes.count()
    
    # Statistiques par banque
    stats_par_banque = []
    banques = Banque.objects.filter(
        Q(depense_feuilles__isnull=False) | Q(recette_feuilles__isnull=False)
    ).distinct()
    
    for banque in banques:
        depenses_banque = depenses.filter(banque=banque)
        recettes_banque = recettes.filter(banque=banque)
        
        total_dep_cdf = depenses_banque.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
        total_dep_usd = depenses_banque.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
        total_rec_cdf = recettes_banque.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
        total_rec_usd = recettes_banque.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
        
        stats_par_banque.append({
            'banque': banque,
            'total_depenses_cdf': total_dep_cdf,
            'total_depenses_usd': total_dep_usd,
            'total_recettes_cdf': total_rec_cdf,
            'total_recettes_usd': total_rec_usd,
            'solde_cdf': total_rec_cdf - total_dep_cdf,
            'solde_usd': total_rec_usd - total_dep_usd,
            'nb_operations': depenses_banque.count() + recettes_banque.count()
        })
    
    # Évolution mensuelle : données par mois pour l'année sélectionnée (tous les mois, pas filtré par mois)
    depenses_evol = DepenseFeuille.objects.filter(annee=annee_filter)
    recettes_evol = RecetteFeuille.objects.filter(annee=annee_filter)
    if banque_filter:
        depenses_evol = depenses_evol.filter(banque_id=banque_filter)
        recettes_evol = recettes_evol.filter(banque_id=banque_filter)
    evolution_mensuelle = []
    for mois in range(1, 13):
        dep_mois = depenses_evol.filter(mois=mois)
        rec_mois = recettes_evol.filter(mois=mois)
        
        total_dep_cdf = dep_mois.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
        total_dep_usd = dep_mois.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
        total_rec_cdf = rec_mois.aggregate(total=Sum('montant_fc'))['total'] or Decimal('0.00')
        total_rec_usd = rec_mois.aggregate(total=Sum('montant_usd'))['total'] or Decimal('0.00')
        
        evolution_mensuelle.append({
            'mois': mois,
            'mois_nom': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'][mois-1],
            'depenses_cdf': float(total_dep_cdf),
            'depenses_usd': float(total_dep_usd),
            'recettes_cdf': float(total_rec_cdf),
            'recettes_usd': float(total_rec_usd),
            'solde_cdf': float(total_rec_cdf - total_dep_cdf),
            'solde_usd': float(total_rec_usd - total_dep_usd)
        })
    
    # Top 10 des plus grosses dépenses et recettes
    top_depenses = depenses.order_by('-montant_fc', '-montant_usd')[:10]
    top_recettes = recettes.order_by('-montant_fc', '-montant_usd')[:10]
    
    # Données pour les graphiques
    graph_data = {
        'evolution_mensuelle': evolution_mensuelle,
        'stats_par_banque': [
            {
                'banque': item['banque'].nom_banque,
                'depenses_cdf': float(item['total_depenses_cdf']),
                'depenses_usd': float(item['total_depenses_usd']),
                'recettes_cdf': float(item['total_recettes_cdf']),
                'recettes_usd': float(item['total_recettes_usd']),
                'solde_cdf': float(item['solde_cdf']),
                'solde_usd': float(item['solde_usd'])
            } for item in stats_par_banque
        ]
    }
    
    # Récupérer les années disponibles (inclure l'année en cours pour les valeurs par défaut)
    annees_depenses = list(DepenseFeuille.objects.values_list('annee', flat=True).distinct())
    annees_recettes = list(RecetteFeuille.objects.values_list('annee', flat=True).distinct())
    annees_disponibles = sorted(set(annees_depenses + annees_recettes + [current_year]), reverse=True)
    
    context = {
        'total_depenses_cdf': total_depenses_cdf,
        'total_depenses_usd': total_depenses_usd,
        'total_recettes_cdf': total_recettes_cdf,
        'total_recettes_usd': total_recettes_usd,
        'solde_cdf': solde_cdf,
        'solde_usd': solde_usd,
        'nb_depenses': nb_depenses,
        'nb_recettes': nb_recettes,
        'stats_par_banque': stats_par_banque,
        'evolution_mensuelle': evolution_mensuelle,
        'top_depenses': top_depenses,
        'top_recettes': top_recettes,
        'graph_data': json.dumps(graph_data),
        'banques': banques,
        'current_year': current_year,
        'current_month': current_month,
        'default_year': default_year,
        'annee_filter': annee_filter,  # Sera None par défaut (toutes les années)
        'mois_filter': mois_filter,
        'banque_filter': banque_filter,
        'mois_choices': [(i, ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]) for i in range(1, 13)],
        'annees_disponibles': annees_disponibles,
        # Ajout des fonctions de formatage
        'format_montant': format_montant,
        'format_montant_decimal': format_montant_decimal,
    }
    
    return render(request, 'tableau_bord_feuilles/dashboard.html', context)


def detail_operations(request):
    """
    Vue détaillée des opérations avec pagination et filtres
    """
    
    # Récupérer les filtres
    annee_filter = request.GET.get('annee')
    mois_filter = request.GET.get('mois')
    banque_filter = request.GET.get('banque')
    type_filter = request.GET.get('type')  # 'depense' ou 'recette'
    search = request.GET.get('search', '')
    
    # Récupérer les données
    depenses = DepenseFeuille.objects.all()
    recettes = RecetteFeuille.objects.all()
    
    # Récupérer les années disponibles sans union
    annees_depenses = list(depenses.values_list('annee', flat=True).distinct())
    annees_recettes = list(recettes.values_list('annee', flat=True).distinct())
    annees_disponibles = sorted(set(annees_depenses + annees_recettes), reverse=True)
    
    # Appliquer les filtres
    if annee_filter:
        annee_filter = int(annee_filter)
        depenses = depenses.filter(annee=annee_filter)
        recettes = recettes.filter(annee=annee_filter)
    
    if mois_filter:
        mois_filter = int(mois_filter)
        depenses = depenses.filter(mois=mois_filter)
        recettes = recettes.filter(mois=mois_filter)
    
    if banque_filter:
        depenses = depenses.filter(banque_id=banque_filter)
        recettes = recettes.filter(banque_id=banque_filter)
    
    if search:
        depenses = depenses.filter(
            Q(libelle_depenses__icontains=search) |
            Q(nature_economique__titre__icontains=search) |
            Q(banque__nom_banque__icontains=search)
        )
        recettes = recettes.filter(
            Q(libelle_recette__icontains=search) |
            Q(banque__nom_banque__icontains=search)
        )
    
    # Combiner les opérations
    operations = []
    
    if type_filter != 'recette':
        for dep in depenses:
            operations.append({
                'type': 'dépense',
                'date': dep.date,
                'libelle': dep.libelle_depenses,
                'banque': dep.banque.nom_banque if dep.banque else 'N/A',
                'montant_cdf': dep.montant_fc,
                'montant_usd': dep.montant_usd,
                'nature': dep.nature_economique.titre if dep.nature_economique else 'N/A',
                'service': dep.service_beneficiaire.nom_service if dep.service_beneficiaire else 'N/A',
                'observation': dep.observation,
                'objet': dep
            })
    
    if type_filter != 'depense':
        for rec in recettes:
            operations.append({
                'type': 'recette',
                'date': rec.date,
                'libelle': rec.libelle_recette,
                'banque': rec.banque.nom_banque if rec.banque else 'N/A',
                'montant_cdf': rec.montant_fc,
                'montant_usd': rec.montant_usd,
                'nature': '-',
                'service': '-',
                'observation': '-',
                'objet': rec
            })
    
    # Trier par date
    operations.sort(key=lambda x: x['date'], reverse=True)
    
    # Pagination
    paginator = Paginator(operations, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'banques': Banque.objects.all(),
        'annee_filter': annee_filter,
        'mois_filter': mois_filter,
        'banque_filter': banque_filter,
        'type_filter': type_filter,
        'search': search,
        'mois_choices': [(i, ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]) for i in range(1, 13)],
        'annees_disponibles': annees_disponibles,
        # Ajout des fonctions de formatage
        'format_montant': format_montant,
        'format_montant_decimal': format_montant_decimal,
    }
    
    return render(request, 'tableau_bord_feuilles/detail_operations.html', context)


def etats_depenses(request):
    """
    Page des états de dépenses avec tous les boutons de rapport
    """
    try:
        from demandes.models import NatureEconomique
        from accounts.models import Service
        from banques.models import Banque
        
        context = {
            'natures': NatureEconomique.objects.filter(active=True).order_by('code'),
            'services': Service.objects.all().order_by('nom_service'),
            'banques': Banque.objects.filter(active=True).order_by('nom_banque'),
            'mois_choices': [(i, ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]) for i in range(1, 13)],
            'annees_disponibles': range(2020, 2026),
            'format_montant': format_montant,
            'format_montant_decimal': format_montant_decimal,
        }
        
        return render(request, 'tableau_bord_feuilles/etats_depenses.html', context)
    except Exception as e:
        return HttpResponse(f"Erreur dans etats_depenses: {str(e)}", content_type='text/plain')


def etats_recettes(request):
    """
    Page des états de recettes avec tous les boutons de rapport
    """
    try:
        from banques.models import Banque
        
        context = {
            'banques': Banque.objects.filter(active=True).order_by('nom_banque'),
            'mois_choices': [(i, ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                                  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]) for i in range(1, 13)],
            'annees_disponibles': range(2020, 2026),
            'format_montant': format_montant,
            'format_montant_decimal': format_montant_decimal,
        }
        
        return render(request, 'tableau_bord_feuilles/etats_recettes.html', context)
    except Exception as e:
        return HttpResponse(f"Erreur dans etats_recettes: {str(e)}", content_type='text/plain')
