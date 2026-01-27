"""
Filtres personnalisés pour le formatage des montants
"""
from django import template
from decimal import Decimal

register = template.Library()


@register.filter(name='format_montant')
def format_montant(value, devise=''):
    """
    Formate un montant avec séparateurs de milliers et décimales
    Exemple: 1234567.89 -> "1 234 567,89"
    Format français : espaces pour milliers, virgule pour décimales
    """
    if value is None or value == '':
        return "0,00"
    
    try:
        # Convertir en Decimal pour avoir une précision exacte
        if isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif isinstance(value, str):
            # Nettoyer la chaîne avant conversion
            value = value.strip()
            value = value.replace(',', '.')
            value = value.replace(' ', '')
            if not value:
                return "0,00"
            value = Decimal(value)
        elif isinstance(value, Decimal):
            pass  # Déjà un Decimal
        else:
            value = Decimal(str(value))
        
        # Séparer partie entière et décimale
        integer_part = int(abs(value))
        decimal_part = abs(value) - integer_part
        
        # Formater la partie entière avec séparateurs de milliers (espaces)
        integer_str = f"{integer_part:,}"
        integer_str = integer_str.replace(',', ' ')
        
        # Formater la partie décimale (2 décimales)
        decimal_str = f"{decimal_part:.2f}".split('.')[1]
        
        # Assembler avec virgule comme séparateur décimal (format français)
        if value < 0:
            formatted = f"-{integer_str},{decimal_str}"
        else:
            formatted = f"{integer_str},{decimal_str}"
        
        # Retourner avec la devise si fournie
        if devise:
            return f"{formatted} {devise}"
        return formatted
    except (ValueError, TypeError, AttributeError, Exception) as e:
        # En cas d'erreur, retourner une valeur par défaut
        return "0,00"


@register.filter(name='format_montant_simple')
def format_montant_simple(value):
    """
    Formate un montant sans décimales (pour les grands montants)
    Exemple: 1234567 -> "1 234 567"
    """
    # Gérer les valeurs None, 0, ou vides
    if value is None or value == 0 or value == '':
        return "0"
    
    try:
        # Gérer les différents types de valeurs
        if isinstance(value, Decimal):
            num_value = int(value)
        elif isinstance(value, (int, float)):
            num_value = int(value)
        elif isinstance(value, str):
            if not value.strip():
                return "0"
            num_value = int(Decimal(value))
        else:
            # Pour les autres types, essayer de convertir
            num_value = int(float(value))
        
        # Si la valeur est 0, retourner "0"
        if num_value == 0:
            return "0"
        
        # Formater avec séparateurs de milliers (espaces)
        # Utiliser la méthode française avec espaces
        formatted = f"{num_value:,}"
        formatted = formatted.replace(',', ' ')
        return formatted
    except (ValueError, TypeError, AttributeError, OverflowError, ZeroDivisionError):
        # En cas d'erreur, retourner "0" par défaut
        return "0"


@register.filter(name='mul')
def mul(value, arg):
    """
    Multiplie une valeur par un argument
    Exemple: {{ montant|mul:0.03 }} pour calculer 3% du montant
    """
    try:
        from decimal import Decimal
        if value is None:
            return Decimal('0.00')
        if isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, Decimal):
            pass
        else:
            value = Decimal(str(value))
        
        if isinstance(arg, (int, float)):
            arg = Decimal(str(arg))
        elif isinstance(arg, str):
            arg = Decimal(arg)
        elif isinstance(arg, Decimal):
            pass
        else:
            arg = Decimal(str(arg))
        
        return value * arg
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')


@register.filter(name='add')
def add(value, arg):
    """
    Additionne une valeur avec un argument
    Exemple: {{ montant|add:ipr }} pour additionner montant + IPR
    """
    try:
        from decimal import Decimal
        if value is None:
            value = Decimal('0.00')
        if isinstance(value, (int, float)):
            value = Decimal(str(value))
        elif isinstance(value, str):
            value = Decimal(value)
        elif isinstance(value, Decimal):
            pass
        else:
            value = Decimal(str(value))
        
        if arg is None:
            arg = Decimal('0.00')
        if isinstance(arg, (int, float)):
            arg = Decimal(str(arg))
        elif isinstance(arg, str):
            arg = Decimal(arg)
        elif isinstance(arg, Decimal):
            pass
        else:
            arg = Decimal(str(arg))
        
        return value + arg
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Récupère un élément d'un dictionnaire par sa clé
    Exemple: {{ sous_totaux|get_item:code }}
    """
    if dictionary is None:
        return None
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None


@register.filter(name='mois_en_lettres')
def mois_en_lettres(value):
    """
    Convertit un numéro de mois (1-12) en nom de mois en français
    Exemple: 1 -> "Janvier", 12 -> "Décembre"
    """
    if value is None:
        return ""
    
    try:
        mois_num = int(value)
        mois_dict = {
            1: 'Janvier',
            2: 'Février',
            3: 'Mars',
            4: 'Avril',
            5: 'Mai',
            6: 'Juin',
            7: 'Juillet',
            8: 'Août',
            9: 'Septembre',
            10: 'Octobre',
            11: 'Novembre',
            12: 'Décembre',
        }
        return mois_dict.get(mois_num, str(value))
    except (ValueError, TypeError):
        return str(value) if value else ""


@register.filter(name='format_montant_sep')
def format_montant_sep(value, devise=None):
    """
    Formate un nombre avec séparateurs de milliers
    Exemple: 3500000 -> 3,500,000
    """
    try:
        if value is None:
            return "0"
        
        value = Decimal(str(value))
        
        # Formatter avec séparateurs
        if devise == 'CDF':
            formatted = "{:,.0f}".format(value)
        else:
            formatted = "{:,.2f}".format(value)
        
        return formatted
    except (ValueError, TypeError):
        return "0"


@register.filter(name='sum_attr')
def sum_attr(queryset, attr):
    """
    Calcule la somme d'un attribut pour tous les objets d'un queryset
    Exemple: {{ demandes|sum_attr:'montant' }}
    """
    try:
        total = Decimal('0.00')
        for obj in queryset:
            value = getattr(obj, attr, Decimal('0.00'))
            if value is not None:
                total += Decimal(str(value))
        return total
    except (ValueError, TypeError, AttributeError):
        return Decimal('0.00')


def nombre_en_lettres(nombre):
    """
    Convertit un nombre en lettres en français (version simplifiée)
    Exemple: 1234.56 -> "mille deux cent trente-quatre francs cinquante-six centimes"
    """
    if nombre is None or nombre == 0:
        return "zéro francs"
    
    try:
        nombre = Decimal(str(nombre))
        nombre = abs(nombre)
        
        # Séparer partie entière et décimale
        partie_entiere = int(nombre)
        partie_decimale = int(round((nombre - partie_entiere) * 100))
        
        # Dictionnaires pour la conversion
        unites = ['', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six', 'sept', 'huit', 'neuf']
        dizaines_simples = ['', '', 'vingt', 'trente', 'quarante', 'cinquante', 'soixante']
        
        def convertir_deux_chiffres(n):
            """Convertit un nombre de 0 à 99"""
            if n == 0:
                return ''
            if n < 10:
                return unites[n]
            if n < 20:
                exceptions = {
                    10: 'dix', 11: 'onze', 12: 'douze', 13: 'treize', 14: 'quatorze',
                    15: 'quinze', 16: 'seize', 17: 'dix-sept', 18: 'dix-huit', 19: 'dix-neuf'
                }
                return exceptions.get(n, '')
            
            dizaine = n // 10
            unite = n % 10
            
            if dizaine == 7:
                if unite == 0:
                    return 'soixante-dix'
                elif unite == 1:
                    return 'soixante-et-onze'
                else:
                    return 'soixante-' + convertir_deux_chiffres(10 + unite)
            elif dizaine == 8:
                if unite == 0:
                    return 'quatre-vingts'
                else:
                    return 'quatre-vingt-' + unites[unite]
            elif dizaine == 9:
                if unite == 0:
                    return 'quatre-vingt-dix'
                else:
                    return 'quatre-vingt-' + convertir_deux_chiffres(10 + unite)
            else:
                if unite == 0:
                    return dizaines_simples[dizaine]
                elif unite == 1 and dizaine > 1:
                    return dizaines_simples[dizaine] + '-et-un'
                else:
                    return dizaines_simples[dizaine] + '-' + unites[unite]
        
        def convertir_trois_chiffres(n):
            """Convertit un nombre de 0 à 999"""
            if n == 0:
                return ''
            
            centaines = n // 100
            reste = n % 100
            
            resultat = []
            if centaines > 0:
                if centaines == 1:
                    resultat.append('cent')
                else:
                    resultat.append(unites[centaines] + ' cent')
                if reste == 0 and centaines > 1:
                    resultat[-1] += 's'  # "cents" au pluriel
            
            if reste > 0:
                resultat.append(convertir_deux_chiffres(reste))
            
            return ' '.join(resultat)
        
        # Convertir la partie entière
        if partie_entiere == 0:
            texte_entier = 'zéro'
        else:
            groupes = []
            millions = partie_entiere // 1000000
            reste_millions = partie_entiere % 1000000
            milliers = reste_millions // 1000
            reste_milliers = reste_millions % 1000
            
            if millions > 0:
                texte_millions = convertir_trois_chiffres(millions)
                if millions == 1:
                    groupes.append('un million')
                else:
                    groupes.append(texte_millions + ' millions')
            
            if milliers > 0:
                texte_milliers = convertir_trois_chiffres(milliers)
                if milliers == 1:
                    groupes.append('mille')
                else:
                    groupes.append(texte_milliers + ' mille')
            
            if reste_milliers > 0:
                groupes.append(convertir_trois_chiffres(reste_milliers))
            
            texte_entier = ' '.join(groupes)
        
        # Convertir la partie décimale
        texte_decimal = ''
        if partie_decimale > 0:
            texte_decimal = convertir_trois_chiffres(partie_decimale)
            if partie_decimale == 1:
                texte_decimal += ' centime'
            else:
                texte_decimal += ' centimes'
        
        # Assembler
        if texte_decimal:
            return f"{texte_entier} francs et {texte_decimal}"
        else:
            if partie_entiere == 1:
                return f"{texte_entier} franc"
            else:
                return f"{texte_entier} francs"
    
    except (ValueError, TypeError):
        return str(nombre) if nombre else "zéro francs"


@register.filter(name='montant_en_lettres')
def montant_en_lettres(value):
    """
    Convertit un montant en lettres en français
    Exemple: 1234.56 -> "mille deux cent trente-quatre francs cinquante-six centimes"
    """
    return nombre_en_lettres(value)

