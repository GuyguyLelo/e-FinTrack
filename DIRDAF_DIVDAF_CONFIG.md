# ✅ Configuration DirDaf et DivDaf - Accès Limité

## 🔐 Identifiants de connexion

### DirDaf (Directeur Général)
- **Username**: `DirDaf`
- **Password**: `DirDaf123`
- **Rôle**: `DG`

### DivDaf (Chef Division Finance)
- **Username**: `DivDaf`
- **Password**: `DivDaf123`
- **Rôle**: `CD_FINANCE`

## 📋 Permissions configurées

### ✅ ACCÈS AUTORISÉ
- **Uniquement** le tableau de bord feuille
- URL: http://127.0.0.1:8000/tableau-bord-feuilles/

### ❌ ACCÈS BLOQUÉ
- Page d'accueil (`/`) → Redirigé vers `/tableau-bord-feuilles/`
- Demandes (`/demandes/`) → Redirigé vers `/tableau-bord-feuilles/`
- Recettes (`/recettes/`) → Redirigé vers `/tableau-bord-feuilles/`
- Admin Django (`/admin/`) → Redirigé vers `/tableau-bord-feuilles/`
- Tous les autres menus

### 🎯 MENU LIMITÉ
Dans l'interface, ces utilisateurs voient **UNIQUEMENT** :
- ✅ **Tableau de bord** (lien actif)

Les menus suivants sont **MASQUÉS** :
- ❌ Natures Économiques
- ❌ Gestion dépenses
- ❌ Gestion recettes
- ❌ Rapports feuilles

## 🛠️ Implémentation technique

### 1. Modèle User (accounts/models.py)
```python
def peut_voir_uniquement_tableau_bord_feuille(self):
    """Vérifie si l'utilisateur ne peut voir que le tableau de bord feuille"""
    return self.role in ['DG', 'CD_FINANCE']
```

### 2. Template (templates/base.html)
```html
{% if user.peut_voir_uniquement_tableau_bord_feuille %}
<!-- DG et CD_FINANCE : uniquement tableau de bord feuille -->
<a class="nav-link" href="{% url 'tableau_bord_feuilles:tableau_bord_feuilles' %}">
    <i class="bi bi-speedometer2"></i> Tableau de bord
</a>
```

### 3. Middleware (accounts/middleware.py)
```python
# Redirection pour DG et CD_FINANCE : uniquement tableau de bord feuille
elif user.role in ['DG', 'CD_FINANCE']:
    allowed_urls = [
        '/tableau-bord-feuilles/',
        '/accounts/logout/',
        '/static/',
        '/media/',
    ]
    
    if not any(request.path.startswith(url) for url in allowed_urls):
        return redirect('/tableau-bord-feuilles/')
```

## 🧪 Tests de validation

### Scripts de test disponibles
- `test_dirdaf_divdaf.py` - Test des permissions
- `test_web_access.py` - Test d'accès web complet

### Résultats des tests
```
✅ Login réussi
✅ Accès '/' redirigé vers '/tableau-bord-feuilles/'
✅ Accès '/tableau-bord-feuilles/' autorisé
✅ Accès '/demandes/' redirigé vers '/tableau-bord-feuilles/'
✅ Accès '/recettes/' redirigé vers '/tableau-bord-feuilles/'
✅ Menu limité à 'Tableau de bord' uniquement
```

## 🚀 Comment utiliser

1. **Démarrer le serveur**:
```bash
source venv/bin/activate
python manage.py runserver
```

2. **Se connecter**:
   - DirDaf: http://127.0.0.1:8000/tableau-bord-feuilles/
   - DivDaf: http://127.0.0.1:8000/tableau-bord-feuilles/

3. **Résultat**:
   - Accès direct au tableau de bord feuille
   - Menu limité à une seule option
   - Toutes les autres URLs redirigées automatiquement

## 🎯 Objectif atteint

Les utilisateurs `DirDaf` et `DivDaf` peuvent maintenant :
- ✅ Voir **UNIQUEMENT** le tableau de bord feuille
- ✅ Accéder à l'application sans voir les autres menus
- ✅ Être redirigés automatiquement s'ils tentent d'accéder à d'autres pages

La configuration est **terminée et fonctionnelle** !
