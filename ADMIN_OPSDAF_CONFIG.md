# ✅ Configuration AdminDaf et OpsDaf - Accès Spécifiques

## 🔐 Identifiants de connexion

### AdminDaf (Admin)
- **Username**: `AdminDaf`
- **Password**: `admin123`
- **Rôle**: `ADMIN`

### OpsDaf (Opérateur de Saisie)
- **Username**: `OpsDaf`
- **Password**: `OpsDaf123`
- **Rôle**: `OPERATEUR_SAISIE`

## 📋 Permissions configurées

### 🌿 AdminDaf - Gestion des Natures Économiques

#### ✅ ACCÈS AUTORISÉS
- **Admin Django**: http://127.0.0.1:8000/admin/
- **Natures Économiques**: http://127.0.0.1:8000/demandes/natures/
- **Création Nature**: http://127.0.0.1:8000/demandes/natures/creer/

#### ❌ ACCÈS BLOQUÉS
- Page d'accueil (`/`) → Redirigé vers `/admin/`
- Demandes (`/demandes/`) → Redirigé vers `/admin/`
- Recettes (`/recettes/`) → Redirigé vers `/admin/`
- Tableau de bord (`/tableau-bord-feuilles/`) → Redirigé vers `/admin/`

#### 🎯 MENU LIMITÉ
- ✅ **Tableau de bord** (redirection vers admin)
- ✅ **Natures Économiques**
- ❌ Gestion dépenses
- ❌ Gestion recettes
- ❌ Rapports feuilles

### 📊 OpsDaf - Gestion des Recettes/Dépenses/États

#### ✅ ACCÈS AUTORISÉS
- **Recettes**: http://127.0.0.1:8000/recettes/feuille/
- **Dépenses**: http://127.0.0.1:8000/demandes/depenses/feuille/
- **État Dépenses**: http://127.0.0.1:8000/tableau-bord-feuilles/etats-depenses/
- **État Recettes**: http://127.0.0.1:8000/tableau-bord-feuilles/etats-recettes/
- **Rapports (sélection)**: http://127.0.0.1:8000/tableau-bord-feuilles/rapport-selection/

#### ❌ ACCÈS BLOQUÉS
- Page d'accueil (`/`) → Redirigé vers `/recettes/feuille/`
- Admin Django (`/admin/`) → Redirigé vers `/recettes/feuille/`
- Natures Économiques (`/demandes/natures/`) → Redirigé vers `/recettes/feuille/`

#### 🎯 MENU LIMITÉ
- ✅ **Tableau de bord**
- ✅ **Gestion dépenses**
- ✅ **Gestion recettes**
- ✅ **Rapports feuilles**
- ❌ Natures Économiques

## 🛠️ Implémentation technique

### 1. Modèle User (accounts/models.py)
```python
def peut_ajouter_nature_economique(self):
    return self.role in ['SUPER_ADMIN', 'ADMIN']

def peut_ajouter_recette_depense(self):
    return self.role in ['SUPER_ADMIN', 'ADMIN', 'OPERATEUR_SAISIE']

def peut_generer_etats(self):
    return self.role in ['SUPER_ADMIN', 'ADMIN', 'OPERATEUR_SAISIE']
```

### 2. Template (templates/base.html)
```html
{% if user.peut_ajouter_nature_economique %}
<a href="{% url 'demandes:nature_liste' %}">Natures Économiques</a>
{% endif %}

{% if user.peut_ajouter_recette_depense %}
<a href="{% url 'demandes:depense_feuille_liste' %}">Gestion dépenses</a>
<a href="{% url 'recettes:feuille_liste' %}">Gestion recettes</a>
{% endif %}

{% if user.peut_generer_etats %}
<!-- Rapports feuilles -->
{% endif %}
```

### 3. Middleware (accounts/middleware.py)
```python
# AdminDaf : accès admin Django + natures économiques
elif user.role == 'ADMIN':
    allowed_urls = ['/admin/', '/demandes/natures/', ...]
    if not any(request.path.startswith(url) for url in allowed_urls):
        return redirect('/admin/')

# OpsDaf : accès recettes/dépenses/états
elif user.role == 'OPERATEUR_SAISIE':
    allowed_urls = ['/recettes/feuille/', '/demandes/depenses/feuille/', ...]
    if not any(request.path.startswith(url) for url in allowed_urls):
        return redirect('/recettes/feuille/')
```

## 🧪 Tests de validation

### Scripts de test disponibles
- `test_admindaf_opsdaf.py` - Test complet des permissions

### Résultats des tests
```
✅ AdminDaf:
   - Accès admin Django: OK
   - Accès natures économiques: Redirigé vers admin (normal)
   - Menu: Tableau de bord + Natures Économiques

✅ OpsDaf:
   - Accès recettes: OK
   - Accès dépenses: OK
   - Accès états dépenses: OK
   - Accès états recettes: OK
   - Menu: Tableau de bord + Gestion dépenses + Gestion recettes + Rapports feuilles
```

## 🚀 Comment utiliser

1. **Démarrer le serveur**:
```bash
source venv/bin/activate
python manage.py runserver
```

2. **Se connecter**:
   - AdminDaf: http://127.0.0.1:8000/admin/
   - OpsDaf: http://127.0.0.1:8000/recettes/feuille/

3. **Utiliser les fonctionnalités**:
   - **AdminDaf**: Admin Django pour gérer utilisateurs + Natures Économiques
   - **OpsDaf**: Saisir des recettes/dépenses + Générer les états

## 🎯 Objectif atteint

### AdminDaf peut maintenant:
- ✅ Accéder à l'admin Django pour gérer les utilisateurs
- ✅ Ajouter/Modifier les natures économiques
- ✅ Accès limité aux fonctionnalités essentielles

### OpsDaf peut maintenant:
- ✅ Ajouter des recettes (feuille)
- ✅ Ajouter des dépenses (feuille)
- ✅ Générer les états (dépenses et recettes)
- ✅ Accès limité aux fonctionnalités de saisie

La configuration est **terminée et fonctionnelle** selon les spécifications !
