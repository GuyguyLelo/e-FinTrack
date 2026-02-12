from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from django.contrib.humanize.templatetags.humanize import intcomma

from demandes.models import DepenseFeuille, NatureEconomique
from recettes.models import RecetteFeuille
from banques.models import Banque
from .forms_rapports import RapportFeuilleSelectionForm


def format_montant_pdf(montant):
    """Formater un montant pour le PDF avec séparateurs de milliers"""
    if montant:
        return f"{intcomma(montant)}"
    return "0"


def _get_param(request, get_name, post_name):
    """Récupère un paramètre depuis GET (priorité) ou POST (noms formulaire)."""
    value = request.GET.get(get_name) or request.POST.get(post_name) or request.POST.get(get_name)
    return value


def _get_param_list(request, post_name, get_name=None):
    """Récupère une liste (multi-select) depuis POST ou depuis GET (valeurs séparées par des virgules)."""
    post_list = request.POST.getlist(post_name)
    if post_list:
        return post_list
    get_val = request.GET.get(get_name or post_name)
    if get_val:
        return [x.strip() for x in str(get_val).split(',') if x.strip()]
    return []


def _queryset_depenses_filtre(request):
    """Construit le queryset DepenseFeuille en appliquant tous les filtres (GET ou POST)."""
    annee = _get_param(request, 'annee', 'annee_depenses')
    mois = _get_param(request, 'mois', 'mois_depenses')
    banques = _get_param(request, 'banques', 'banques_depenses')
    natures = _get_param(request, 'natures', 'natures_depenses')
    services = _get_param(request, 'services', 'services_depenses')
    montant_min = _get_param(request, 'montant_min', 'montant_min_depenses')
    montant_max = _get_param(request, 'montant_max', 'montant_max_depenses')
    observation = _get_param(request, 'observation', 'observation_depenses')

    qs = DepenseFeuille.objects.all()
    if annee and str(annee).isdigit() and annee != '':
        qs = qs.filter(annee=int(annee))
    if mois and str(mois).isdigit() and mois != '':
        qs = qs.filter(mois=int(mois))
    if banques and str(banques).isdigit() and banques != '':
        qs = qs.filter(banque_id=int(banques))
    if natures and str(natures).isdigit() and natures != '':
        qs = qs.filter(nature_economique_id=int(natures))
    if services and str(services).isdigit() and services != '':
        qs = qs.filter(service_beneficiaire_id=int(services))
    if montant_min and str(montant_min).replace('.', '').replace('-', '').isdigit():
        qs = qs.filter(montant_fc__gte=Decimal(str(montant_min)))
    if montant_max and str(montant_max).replace('.', '').replace('-', '').isdigit():
        qs = qs.filter(montant_fc__lte=Decimal(str(montant_max)))
    if observation and observation.strip():
        qs = qs.filter(observation__icontains=observation.strip())
    return qs.order_by('date')


def _queryset_recettes_filtre(request):
    """Construit le queryset RecetteFeuille en appliquant tous les filtres (GET ou POST)."""
    annee = _get_param(request, 'annee', 'annee_recettes')
    mois = _get_param(request, 'mois', 'mois_recettes')
    banques = _get_param(request, 'banques', 'banques_recettes')
    libelle = _get_param(request, 'libelle', 'libelle_recettes')
    montant_min = _get_param(request, 'montant_min', 'montant_min_recettes')
    montant_max = _get_param(request, 'montant_max', 'montant_max_recettes')
    montant_usd_min = _get_param(request, 'montant_usd_min', 'montant_usd_min_recettes')
    montant_usd_max = _get_param(request, 'montant_usd_max', 'montant_usd_max_recettes')

    qs = RecetteFeuille.objects.all()
    if annee and str(annee).isdigit() and annee != '':
        qs = qs.filter(annee=int(annee))
    if mois and str(mois).isdigit() and mois != '':
        qs = qs.filter(mois=int(mois))
    if banques and str(banques).isdigit() and banques != '':
        qs = qs.filter(banque_id=int(banques))
    if libelle and libelle.strip():
        qs = qs.filter(libelle_recette__icontains=libelle.strip())
    if montant_min and str(montant_min).replace('.', '').replace('-', '').isdigit():
        qs = qs.filter(montant_fc__gte=Decimal(str(montant_min)))
    if montant_max and str(montant_max).replace('.', '').replace('-', '').isdigit():
        qs = qs.filter(montant_fc__lte=Decimal(str(montant_max)))
    if montant_usd_min and str(montant_usd_min).replace('.', '').replace('-', '').isdigit():
        qs = qs.filter(montant_usd__gte=Decimal(str(montant_usd_min)))
    if montant_usd_max and str(montant_usd_max).replace('.', '').replace('-', '').isdigit():
        qs = qs.filter(montant_usd__lte=Decimal(str(montant_usd_max)))
    return qs.order_by('date')


class RapportFeuilleSelectionView(LoginRequiredMixin, View):
    """Vue pour la sélection des rapports feuilles avec la logique des états"""
    template_name = 'tableau_bord_feuilles/rapport_selection.html'
    
    def get(self, request, *args, **kwargs):
        # Récupérer les années disponibles
        from demandes.models import DepenseFeuille
        from recettes.models import RecetteFeuille
        
        annees_depenses = list(DepenseFeuille.objects.values_list('annee', flat=True).distinct())
        annees_recettes = list(RecetteFeuille.objects.values_list('annee', flat=True).distinct())
        annees_disponibles = sorted(set(annees_depenses + annees_recettes), reverse=True)
        
        # Créer le formulaire avec les années disponibles
        form = RapportFeuilleSelectionForm(annees_disponibles=annees_disponibles)
        
        context = {
            'form': form,
            'annees_disponibles': annees_disponibles,
        }
        
        return render(request, self.template_name, context)


class RapportRecetteFeuillePDFView(LoginRequiredMixin, View):
    """Vue pour générer le PDF des recettes feuilles (tous les paramètres du formulaire appliqués)."""
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        recettes = _queryset_recettes_filtre(request)
        if not recettes.exists():
            return HttpResponse("Aucune recette trouvée pour les critères sélectionnés.", status=404)

        annee = _get_param(request, 'annee', 'annee_recettes')
        mois_param = _get_param_list(request, 'mois_recettes', 'mois')
        if annee and str(annee).isdigit():
            annee = int(annee)
        else:
            annee = recettes.order_by('annee').values_list('annee', flat=True).first() or timezone.now().year
        if mois_param and all(str(m).isdigit() for m in mois_param):
            mois_int = int(mois_param[0])
        else:
            premier = recettes.order_by('mois').values_list('mois', flat=True).first()
            mois_int = int(premier) if premier else timezone.now().month
        
        response = HttpResponse(content_type='application/pdf')
        filename = f"rapport_recettes_{annee}_{mois_int:02d}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Créer le document PDF en mode paysage
        doc = SimpleDocTemplate(response, pagesize=landscape(A4), rightMargin=2*cm, leftMargin=2*cm, 
                              topMargin=2*cm, bottomMargin=2*cm)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Contenu du PDF
        story = []
        
        # Titre
        mois_nom = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][mois_int - 1]
        story.append(Paragraph("RAPPORT DES RECETTES", title_style))
        story.append(Paragraph(f"Période: {mois_nom} {annee}", subtitle_style))
        story.append(Spacer(1, 20))
        
        
        # Tableau détaillé des recettes
        story.append(Paragraph("DÉTAIL DES RECETTES", subtitle_style))
        story.append(Spacer(1, 12))
        
        # En-têtes du tableau
        headers = ['Date', 'Libellé', 'Banque', 'Montant CDF', 'Montant USD']
        data = [headers]
        
        # Données
        for recette in recettes:
            data.append([
                recette.date.strftime('%d/%m/%Y'),
                recette.libelle_recette[:50] + '...' if len(recette.libelle_recette) > 50 else recette.libelle_recette,
                recette.banque.nom_banque if recette.banque else 'N/A',
                format_montant_pdf(recette.montant_fc),
                format_montant_pdf(recette.montant_usd)
            ])
        
        # Créer le tableau avec plus de colonnes pour le mode paysage
        table = Table(data, colWidths=[3*cm, 8*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (3, 1), (4, -1), 'RIGHT'),
        ]))
        
        story.append(table)
        
        # Pied de page
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                             ParagraphStyle('Footer', parent=styles['Normal'], 
                                           fontSize=8, alignment=TA_CENTER, textColor=colors.black)))
        
        # Générer le PDF
        doc.build(story)
        
        return response


class RapportDepenseFeuillePDFView(LoginRequiredMixin, View):
    """Vue pour générer le PDF des dépenses feuilles (tous les paramètres du formulaire appliqués)."""
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        depenses = _queryset_depenses_filtre(request)
        if not depenses.exists():
            return HttpResponse("Aucune dépense trouvée pour les critères sélectionnés.", status=404)

        # Pour le titre et le nom de fichier : utiliser la période (premier enregistrement ou paramètres)
        annee = _get_param(request, 'annee', 'annee_depenses')
        mois_param = _get_param_list(request, 'mois_depenses', 'mois')
        if annee and str(annee).isdigit():
            annee = int(annee)
        else:
            annee = depenses.order_by('annee').values_list('annee', flat=True).first() or timezone.now().year
        if mois_param and all(str(m).isdigit() for m in mois_param):
            mois_int = int(mois_param[0])
        else:
            premier = depenses.order_by('mois').values_list('mois', flat=True).first()
            mois_int = int(premier) if premier else timezone.now().month
        
        response = HttpResponse(content_type='application/pdf')
        filename = f"rapport_depenses_{annee}_{mois_int:02d}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Créer le document PDF en mode paysage
        doc = SimpleDocTemplate(response, pagesize=landscape(A4), rightMargin=2*cm, leftMargin=2*cm, 
                              topMargin=2*cm, bottomMargin=2*cm)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.black
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Contenu du PDF
        story = []
        
        # Titre
        mois_nom = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                   'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][mois_int - 1]
        story.append(Paragraph("RAPPORT DES DÉPENSES", title_style))
        story.append(Paragraph(f"Période: {mois_nom} {annee}", subtitle_style))
        story.append(Spacer(1, 20))
        
        
        # Tableau détaillé des dépenses
        story.append(Paragraph("DÉTAIL DES DÉPENSES", subtitle_style))
        story.append(Spacer(1, 12))
        
        # En-têtes du tableau
        headers = ['Date', 'Libellé', 'Nature', 'Banque', 'Montant CDF', 'Montant USD']
        data = [headers]
        
        # Données
        for depense in depenses:
            data.append([
                depense.date.strftime('%d/%m/%Y'),
                depense.libelle_depenses[:40] + '...' if len(depense.libelle_depenses) > 40 else depense.libelle_depenses,
                depense.nature_economique.titre[:30] + '...' if depense.nature_economique and len(depense.nature_economique.titre) > 30 else (depense.nature_economique.titre if depense.nature_economique else 'N/A'),
                depense.banque.nom_banque if depense.banque else 'N/A',
                format_montant_pdf(depense.montant_fc),
                format_montant_pdf(depense.montant_usd)
            ])
        
        # Créer le tableau avec plus de colonnes pour le mode paysage
        table = Table(data, colWidths=[3*cm, 6*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (4, 1), (5, -1), 'RIGHT'),
        ]))
        
        story.append(table)
        
        # Pied de page
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                             ParagraphStyle('Footer', parent=styles['Normal'], 
                                           fontSize=8, alignment=TA_CENTER, textColor=colors.black)))
        
        # Générer le PDF
        doc.build(story)
        
        return response
