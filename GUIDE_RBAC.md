# 🎯 Système de Gestion des Rôles et Permissions (RBAC)

## 📋 Vue d'ensemble

Le système RBAC (Role-Based Access Control) permet une gestion **dynamique et flexible** des rôles et permissions dans l'application e-FinTrack.

### 🔧 **Composants principaux**

#### 1. **Modèles**
- **Permission** : Définit une permission spécifique du système
- **Role** : Définit un rôle avec ses permissions
- **RolePermission** : Table de liaison entre rôles et permissions
- **UserProfile** : Profil utilisateur lié à un rôle

#### 2. **Interface d'administration**
- URL : `/rbac/roles/` - Gestion des rôles
- URL : `/rbac/permissions/` - Gestion des permissions
- URL : `/rbac/roles/<id>/permissions/` - Gestion des permissions d'un rôle

#### 3. **Permissions de base créées**
- **35 permissions** couvrant tous les modules
- **6 rôles système** avec permissions pré-configurées

## 🎨 **Exemple d'utilisation pour les DAF**

### Cas pratique : Les utilisateurs DAF

#### 📊 **Rôles DAF disponibles**
1. **Administrateur DAF** (`ADMIN_DAF`)
   - Voir tableau de bord ✅
   - Voir tableau de bord feuille ✅
   - Gérer les demandes et paiements ✅
   - Accès complet aux modules financiers ✅

2. **Directeur DAF** (`DIR_DAF`)
   - Voir tableau de bord feuille ✅
   - Créer et modifier demandes ✅
   - Gérer les paiements ✅
   - Voir les états et clôtures ✅

3. **Division DAF** (`DIV_DAF`)
   - Voir tableau de bord feuille ✅
   - Gérer les demandes et paiements ✅
   - Accès limité (pas de clôtures) ✅

4. **Opération DAF** (`OPS_DAF`)
   - Saisie des demandes et paiements ✅
   - Accès aux états et rapports ✅

### 🔧 **Comment modifier les permissions**

#### Étape 1 : Accéder à la gestion des rôles
```
URL : http://127.0.0.1:8001/rbac/roles/
```

#### Étape 2 : Sélectionner un rôle DAF
```
Cliquez sur "Permissions" dans la liste des rôles
Exemple : Cliquez sur le bouton 🗝️ à côté de "Directeur DAF"
```

#### Étape 3 : Gérer les permissions
```
Interface à deux colonnes :
- Gauche : Permissions actuelles du rôle
- Droite : Permissions disponibles à ajouter

Pour ajouter une permission :
1. Cherchez dans la liste de droite
2. Cliquez sur ➕ pour ajouter
3. Pour retirer : Cliquez sur 🗑️
```

#### Étape 4 : Exemples de modifications

**Scénario 1 : Ajouter l'accès aux clôtures**
```
1. Allez dans "Permissions disponibles"
2. Trouvez "Effectuer clôtures"
3. Cliquez ➕ pour l'ajouter au rôle DIR_DAF
```

**Scénario 2 : Retirer l'accès à la création d'utilisateurs**
```
1. Dans "Permissions actuelles"
2. Trouvez "Créer utilisateurs"
3. Cliquez 🗑️ pour la retirer du rôle DIV_DAF
```

## 🎯 **Avantages du système**

### ✅ **Flexibilité totale**
- Créer des rôles personnalisés
- Modifier les permissions en temps réel
- Pas besoin de modifier le code

### ✅ **Traçabilité**
- Historique des attributions de permissions
- Qui a quoi et depuis quand

### ✅ **Sécurité**
- Contrôle granulaire des accès
- Permissions activables/désactivables

### ✅ **Évolutivité**
- Ajouter de nouvelles permissions facilement
- Créer de nouveaux rôles selon les besoins

## 🔗 **Intégration avec le code existant**

### Vérification des permissions en code
```python
# Dans une vue ou middleware
from rbac.models import UserProfile

def ma_vue(request):
    try:
        profile = request.user.userprofile
        if profile.a_permission('voir_tableau_bord_feuille'):
            # L'utilisateur a la permission
            return render(request, 'tableau_bord.html')
        else:
            # Permission refusée
            return redirect('access_denied')
    except UserProfile.DoesNotExist:
        # L'utilisateur n'a pas de profil RBAC
        return redirect('create_profile')
```

### Middleware de permissions
```python
class RBACMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier les permissions basées sur le rôle
        if hasattr(request.user, 'userprofile'):
            profile = request.user.userprofile
            request.permissions = profile.get_permissions_codes()
        
        response = self.get_response(request)
        return response
```

## 🚀 **Prochaines étapes**

1. **Intégration complète** avec les vues existantes
2. **Migration des utilisateurs** vers le nouveau système
3. **Interface utilisateur** pour auto-assignation
4. **API REST** pour la gestion des permissions
5. **Templates** avec vérification automatique

## 🎉 **Conclusion**

Le système RBAC offre une **gestion moderne et flexible** des permissions qui permet :
- **Adaptation** aux besoins métier
- **Évolution** sans modification du code
- **Sécurité** granulaire et traçable

Plus besoin de modifier le code source pour gérer les accès ! 🎯
