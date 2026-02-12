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
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.paginator import Paginator
from datetime import datetime
import json

from demandes.models import DepenseFeuille, NatureEconomique
from recettes.models import RecetteFeuille
from banques.models import Banque
from accounts.models import Service


def format_montant_pdf(montant):
    """Formater un montant pour le PDF avec séparateurs de milliers"""
    if montant:
        return f"{intcomma(montant)}"
    return "0"


class TableauGeneralFeuillesView(LoginRequiredMixin, View):
    """Vue pour afficher tous les attributs des feuilles avec filtres"""
    template_name = 'tableau_bord_feuilles/tableau_general.html'
    
    def get(self, request, *args, **kwargs):
        # Récupérer les paramètres de filtrage
        type_filter = request.GET.get('type', '')
        annee_filter = request.GET.get('annee', '')
        mois_filter = request.GET.get('mois', '')
        banque_filter = request.GET.get('banque', '')
        nature_filter = request.GET.get('nature', '')
        service_filter = request.GET.get('service', '')
        date_debut = request.GET.get('date_debut', '')
        date_fin = request.GET.get('date_fin', '')
        search = request.GET.get('search', '')
        
        # Récupérer les données de base
        depenses = DepenseFeuille.objects.all()
        recettes = RecetteFeuille.objects.all()
        
        # Filtrer par type
        if type_filter == 'depense':
            recettes = RecetteFeuille.objects.none()
        elif type_filter == 'recette':
            depenses = DepenseFeuille.objects.none()
        
        # Appliquer les filtres sur les dépenses
        if annee_filter:
            depenses = depenses.filter(annee=annee_filter)
        if mois_filter:
            depenses = depenses.filter(mois=mois_filter)
        if banque_filter:
            depenses = depenses.filter(banque_id=banque_filter)
        if nature_filter:
            depenses = depenses.filter(nature_economique_id=nature_filter)
        if service_filter:
            depenses = depenses.filter(service_beneficiaire_id=service_filter)
        if date_debut:
            depenses = depenses.filter(date__gte=date_debut)
        if date_fin:
            depenses = depenses.filter(date__lte=date_fin)
        if search:
            depenses = depenses.filter(
                Q(libelle_depenses__icontains=search) |
                Q(observation__icontains=search)
            )
        
        # Appliquer les filtres sur les recettes
        if annee_filter:
            recettes = recettes.filter(annee=annee_filter)
        if mois_filter:
            recettes = recettes.filter(mois=mois_filter)
        if banque_filter:
            recettes = recettes.filter(banque_id=banque_filter)
        if date_debut:
            recettes = recettes.filter(date__gte=date_debut)
        if date_fin:
            recettes = recettes.filter(date__lte=date_fin)
        if search:
            recettes = recettes.filter(libelle_recette__icontains=search)
        
        # Combiner et trier
        operations = []
        
        # Ajouter les dépenses
        for dep in depenses:
            operations.append({
                'type': 'dépense',
                'date': dep.date,
                'libelle': dep.libelle_depenses,
                'nature': dep.nature_economique.titre if dep.nature_economique else '',
                'service': dep.service_beneficiaire.nom_service if dep.service_beneficiaire else '',
                'banque': dep.banque.nom_banque if dep.banque else '',
                'montant_cdf': dep.montant_fc,
                'montant_usd': dep.montant_usd,
                'observation': dep.observation,
                'mois': dep.mois,
                'annee': dep.annee,
                'id': dep.id,
            })
        
        # Ajouter les recettes
        for rec in recettes:
            operations.append({
                'type': 'recette',
                'date': rec.date,
                'libelle': rec.libelle_recette,
                'nature': '',
                'service': '',
                'banque': rec.banque.nom_banque if rec.banque else '',
                'montant_cdf': rec.montant_fc,
                'montant_usd': rec.montant_usd,
                'observation': '',
                'mois': rec.mois,
                'annee': rec.annee,
                'id': rec.id,
            })
        
        # Trier par date
        operations.sort(key=lambda x: x['date'], reverse=True)
        
        # Pagination
        paginator = Paginator(operations, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Calculer les totaux
        total_depenses_cdf = sum(op['montant_cdf'] for op in operations if op['type'] == 'dépense')
        total_depenses_usd = sum(op['montant_usd'] for op in operations if op['type'] == 'dépense')
        total_recettes_cdf = sum(op['montant_cdf'] for op in operations if op['type'] == 'recette')
        total_recettes_usd = sum(op['montant_usd'] for op in operations if op['type'] == 'recette')
        solde_cdf = total_recettes_cdf - total_depenses_cdf
        solde_usd = total_recettes_usd - total_depenses_usd
        
        # Récupérer les données pour les filtres
        annees_disponibles = sorted(set(
            list(DepenseFeuille.objects.values_list('annee', flat=True).distinct()) +
            list(RecetteFeuille.objects.values_list('annee', flat=True).distinct())
        ), reverse=True)
        
        context = {
            'page_obj': page_obj,
            'total_depenses_cdf': total_depenses_cdf,
            'total_depenses_usd': total_depenses_usd,
            'total_recettes_cdf': total_recettes_cdf,
            'total_recettes_usd': total_recettes_usd,
            'solde_cdf': solde_cdf,
            'solde_usd': solde_usd,
            'banques': Banque.objects.all(),
            'natures': NatureEconomique.objects.all(),
            'services': Service.objects.all(),
            'annees_disponibles': annees_disponibles,
            'mois_choices': [(i, ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][i-1]) for i in range(1, 13)],
            'type_filter': type_filter,
            'annee_filter': annee_filter,
            'mois_filter': mois_filter,
            'banque_filter': banque_filter,
            'nature_filter': nature_filter,
            'service_filter': service_filter,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'search': search,
            'nb_operations': len(operations),
            'nb_depenses': len([op for op in operations if op['type'] == 'dépense']),
            'nb_recettes': len([op for op in operations if op['type'] == 'recette']),
        }
        
        return render(request, self.template_name, context)


class TableauGeneralPDFView(LoginRequiredMixin, View):
    """Vue pour générer le PDF du tableau général filtré"""
    
    def post(self, request, *args, **kwargs):
        # Récupérer les mêmes paramètres de filtrage
        type_filter = request.POST.get('type', '')
        annee_filter = request.POST.get('annee', '')
        mois_filter = request.POST.get('mois', '')
        banque_filter = request.POST.get('banque', '')
        nature_filter = request.POST.get('nature', '')
        service_filter = request.POST.get('service', '')
        date_debut = request.POST.get('date_debut', '')
        date_fin = request.POST.get('date_fin', '')
        search = request.POST.get('search', '')
        
        # Appliquer les mêmes filtres que dans la vue principale
        depenses = DepenseFeuille.objects.all()
        recettes = RecetteFeuille.objects.all()
        
        if type_filter == 'depense':
            recettes = RecetteFeuille.objects.none()
        elif type_filter == 'recette':
            depenses = DepenseFeuille.objects.none()
        
        if annee_filter:
            depenses = depenses.filter(annee=annee_filter)
            recettes = recettes.filter(annee=annee_filter)
        if mois_filter:
            depenses = depenses.filter(mois=mois_filter)
            recettes = recettes.filter(mois=mois_filter)
        if banque_filter:
            depenses = depenses.filter(banque_id=banque_filter)
            recettes = recettes.filter(banque_id=banque_filter)
        if nature_filter:
            depenses = depenses.filter(nature_economique_id=nature_filter)
        if service_filter:
            depenses = depenses.filter(service_beneficiaire_id=service_filter)
        if date_debut:
            depenses = depenses.filter(date__gte=date_debut)
            recettes = recettes.filter(date__gte=date_debut)
        if date_fin:
            depenses = depenses.filter(date__lte=date_fin)
            recettes = recettes.filter(date__lte=date_fin)
        if search:
            depenses = depenses.filter(
                Q(libelle_depenses__icontains=search) |
                Q(observation__icontains=search)
            )
            recettes = recettes.filter(libelle_recette__icontains=search)
        
        # Combiner les données
        operations = []
        
        for dep in depenses:
            operations.append({
                'type': 'dépense',
                'date': dep.date,
                'libelle': dep.libelle_depenses,
                'nature': dep.nature_economique.titre if dep.nature_economique else '',
                'service': dep.service_beneficiaire.nom_service if dep.service_beneficiaire else '',
                'banque': dep.banque.nom_banque if dep.banque else '',
                'montant_cdf': dep.montant_fc,
                'montant_usd': dep.montant_usd,
                'observation': dep.observation,
            })
        
        for rec in recettes:
            operations.append({
                'type': 'recette',
                'date': rec.date,
                'libelle': rec.libelle_recette,
                'nature': '',
                'service': '',
                'banque': rec.banque.nom_banque if rec.banque else '',
                'montant_cdf': rec.montant_fc,
                'montant_usd': rec.montant_usd,
                'observation': '',
            })
        
        # Trier par date
        operations.sort(key=lambda x: x['date'], reverse=True)
        
        if not operations:
            return HttpResponse("Aucune opération trouvée pour les filtres sélectionnés", status=404)
        
        # Créer le PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"tableau_general_feuilles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Document PDF en mode paysage
        doc = SimpleDocTemplate(response, pagesize=landscape(A4), rightMargin=1.5*cm, leftMargin=1.5*cm, 
                              topMargin=2*cm, bottomMargin=2*cm)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_CENTER
        )
        
        # Contenu du PDF
        story = []
        
        # Titre
        story.append(Paragraph("TABLEAU GÉNÉRAL DES FEUILLES", title_style))
        
        # Période/filtres
        filtre_texte = "Filtres: "
        if type_filter:
            filtre_texte += f"Type: {type_filter}, "
        if annee_filter:
            filtre_texte += f"Année: {annee_filter}, "
        if mois_filter:
            mois_nom = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'][int(mois_filter)-1]
            filtre_texte += f"Mois: {mois_nom}, "
        if banque_filter:
            banque = Banque.objects.get(id=banque_filter)
            filtre_texte += f"Banque: {banque.nom_banque}, "
        if nature_filter:
            nature = NatureEconomique.objects.get(id=nature_filter)
            filtre_texte += f"Nature: {nature.titre}, "
        if service_filter:
            service = Service.objects.get(id=service_filter)
            filtre_texte += f"Service: {service.nom_service}, "
        if date_debut and date_fin:
            filtre_texte += f"Période: {date_debut} au {date_fin}, "
        elif date_debut:
            filtre_texte += f"À partir du: {date_debut}, "
        elif date_fin:
            filtre_texte += f"Jusqu'au: {date_fin}, "
        if search:
            filtre_texte += f"Recherche: {search}, "
        
        if filtre_texte.endswith(", "):
            filtre_texte = filtre_texte[:-2]
        
        story.append(Paragraph(filtre_texte, subtitle_style))
        story.append(Spacer(1, 15))
        
        # Statistiques
        total_depenses_cdf = sum(op['montant_cdf'] for op in operations if op['type'] == 'dépense')
        total_depenses_usd = sum(op['montant_usd'] for op in operations if op['type'] == 'dépense')
        total_recettes_cdf = sum(op['montant_cdf'] for op in operations if op['type'] == 'recette')
        total_recettes_usd = sum(op['montant_usd'] for op in operations if op['type'] == 'recette')
        solde_cdf = total_recettes_cdf - total_depenses_cdf
        solde_usd = total_recettes_usd - total_depenses_usd
        nb_depenses = len([op for op in operations if op['type'] == 'dépense'])
        nb_recettes = len([op for op in operations if op['type'] == 'recette'])
        
        story.append(Paragraph(f"<b>Nombre d'opérations:</b> {len(operations)} (Dépenses: {nb_depenses}, Recettes: {nb_recettes})", subtitle_style))
        story.append(Paragraph(f"<b>Total Dépenses:</b> {format_montant_pdf(total_depenses_cdf)} CDF / {format_montant_pdf(total_depenses_usd)} USD", subtitle_style))
        story.append(Paragraph(f"<b>Total Recettes:</b> {format_montant_pdf(total_recettes_cdf)} CDF / {format_montant_pdf(total_recettes_usd)} USD", subtitle_style))
        story.append(Paragraph(f"<b>Solde Net:</b> {format_montant_pdf(solde_cdf)} CDF / {format_montant_pdf(solde_usd)} USD", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Tableau détaillé
        story.append(Paragraph("DÉTAIL DES OPÉRATIONS", subtitle_style))
        story.append(Spacer(1, 10))
        
        # En-têtes du tableau
        headers = ['Date', 'Type', 'Libellé', 'Nature', 'Service', 'Banque', 'Montant CDF', 'Montant USD', 'Observation']
        data = [headers]
        
        # Données
        for op in operations:
            data.append([
                op['date'].strftime('%d/%m/%Y'),
                op['type'].upper(),
                op['libelle'][:40] + '...' if len(op['libelle']) > 40 else op['libelle'],
                op['nature'][:20] + '...' if len(op['nature']) > 20 else op['nature'],
                op['service'][:15] + '...' if len(op['service']) > 15 else op['service'],
                op['banque'][:15] + '...' if len(op['banque']) > 15 else op['banque'],
                format_montant_pdf(op['montant_cdf']),
                format_montant_pdf(op['montant_usd']),
                op['observation'][:30] + '...' if len(op['observation']) > 30 else op['observation'],
            ])
        
        # Créer le tableau
        table = Table(data, colWidths=[2.5*cm, 1.5*cm, 6*cm, 2.5*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            ('ALIGN', (5, 1), (5, -1), 'LEFT'),
            ('ALIGN', (8, 1), (8, -1), 'LEFT'),
            ('ALIGN', (6, 1), (7, -1), 'RIGHT'),
        ]))
        
        # Couleurs pour les types
        for i, row in enumerate(data[1:], start=1):
            if row[1] == 'DÉPENSE':
                table.setStyle(TableStyle([('TEXTCOLOR', (0, i), (-1, i), colors.red)]))
            else:
                table.setStyle(TableStyle([('TEXTCOLOR', (0, i), (-1, i), colors.green)]))
        
        story.append(table)
        
        # Pied de page
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 
                             ParagraphStyle('Footer', parent=styles['Normal'], 
                                           fontSize=8, alignment=TA_CENTER, textColor=colors.grey)))
        
        # Générer le PDF
        doc.build(story)
        
        return response
