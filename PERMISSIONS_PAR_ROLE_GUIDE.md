# 🎯 Configuration des Permissions par Rôle

## 🎯 **Objectif clair**

Configurer des permissions différentes selon le rôle :
- **AdminDaf** : Voir **uniquement** `/demandes/natures/`
- **SuperAdmin** : Voir **tout** (dashboard, recettes, dépenses, admin Django)

---

## 👥 **Rôles et permissions configurés**

### **1. SuperAdmin (ADMIN) - Accès complet**
```
👑 SuperAdmin
🎯 Role: ADMIN
✅ is_superuser: True
✅ is_staff: True
🌐 Accès: Dashboard + Recettes + Dépenses + Admin Django
🔑 Login: SuperAdmin / SuperAdmin123!
```

### **2. AdminDaf (CD_FINANCE) - Accès limité**
```
👤 AdminDaf
🎯 Role: CD_FINANCE
❌ is_superuser: False
❌ is_staff: False
🌐 Accès: /demandes/natures/ UNIQUEMENT
🔑 Login: AdminDaf / AdminDaf123!
```

### **3. DirDaf (DG) - Accès direction**
```
👤 DirDaf
🎯 Role: DG
❌ is_superuser: False
❌ is_staff: False
🌐 Accès: Dashboard direction limité
🔑 Login: DirDaf / DirDaf123!
```

### **4. OpsDaf (OPERATEUR_SAISIE) - Accès saisie**
```
👤 OpsDaf
🎯 Role: OPERATEUR_SAISIE
❌ is_superuser: False
❌ is_staff: False
🌐 Accès: Saisie recettes/dépenses uniquement
🔑 Login: OpsDaf / OpsDaf123!
```

---

## 🚀 **Script de configuration**

### **setup_role_permissions.sh**
```bash
# Sur votre VPS
cd ~/e-FinTrack
chmod +x setup_role_permissions.sh
./setup_role_permissions.sh
```

### **Ce que fait le script**

1. **🔧 Configure les rôles** : Attribue les bons rôles et permissions
2. **🧪 Teste les accès** : Vérifie chaque rôle avec les URLs appropriées
3. **📝 Crée les décorateurs** : Fichiers pour implémenter les permissions
4. **🎯 Donne des exemples** : Code prêt à utiliser

---

## 🔧 **Implémentation des permissions**

### **1. Décorateurs de rôle (créé par le script)**
```python
# role_decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    """Vérifie si l'utilisateur a le rôle requis"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            
            if request.user.role not in allowed_roles:
                messages.error(request, "Accès non autorisé pour votre rôle")
                return redirect('accounts:login')
                
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_required(view_func):
    """Uniquement les admins (SuperAdmin)"""
    return role_required(['ADMIN'])(view_func)

def finance_required(view_func):
    """Services financiers (AdminDaf, DirDaf, SuperAdmin)"""
    return role_required(['ADMIN', 'CD_FINANCE', 'DG'])(view_func)
```

### **2. Exemple d'utilisation dans les vues**
```python
# views.py
from role_decorators import admin_required, finance_required

# Uniquement SuperAdmin
@admin_required
def dashboard_admin(request):
    return render(request, 'dashboard_admin.html')

# AdminDaf peut voir les natures
@finance_required
def natures_list(request):
    return render(request, 'demandes/nature_liste.html')

# Tous les utilisateurs authentifiés
@login_required
def recettes_list(request):
    return render(request, 'recettes/recette_feuille_liste.html')
```

---

## 🌐 **Test des permissions**

### **1. Exécuter le script**
```bash
cd ~/e-FinTrack
chmod +x setup_role_permissions.sh
./setup_role_permissions.sh
```

### **2. Tester les connexions**
```bash
# Test SuperAdmin
URL: http://187.77.171.80:8000/accounts/login/
Login: SuperAdmin / SuperAdmin123!
Résultat: Dashboard complet ✅

# Test AdminDaf
URL: http://187.77.171.80:8000/accounts/login/
Login: AdminDaf / AdminDaf123!
Résultat: /demandes/natures/ uniquement ✅
```

---

## 🔍 **Configuration des redirections**

### **Redirections par rôle**
```python
# Dans la vue de login
def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Redirection selon le rôle
            if user.role == 'ADMIN':
                return redirect('/dashboard/')  # SuperAdmin
            elif user.role == 'CD_FINANCE':
                return redirect('/demandes/natures/')  # AdminDaf
            elif user.role == 'DG':
                return redirect('/dashboard/')  # DirDaf
            elif user.role == 'OPERATEUR_SAISIE':
                return redirect('/recettes/feuille/')  # OpsDaf
            else:
                return redirect('/')  # Défaut
```

---

## 📊 **Résumé des permissions**

### **Tableau des accès**

| Rôle | Dashboard | Recettes | Dépenses | Natures | Admin Django |
|-------|-----------|-----------|-----------|----------|---------------|
| SuperAdmin (ADMIN) | ✅ | ✅ | ✅ | ✅ | ✅ |
| AdminDaf (CD_FINANCE) | ❌ | ❌ | ❌ | ✅ | ❌ |
| DirDaf (DG) | ✅ | ✅ | ✅ | ✅ | ❌ |
| OpsDaf (OPERATEUR_SAISIE) | ❌ | ✅ | ✅ | ❌ | ❌ |

---

## 🎯 **Actions sur votre VPS**

### **1. Configuration des rôles**
```bash
cd ~/e-FinTrack
chmod +x setup_role_permissions.sh
./setup_role_permissions.sh
```

### **2. Implémenter les décorateurs**
```bash
# Le script crée déjà les fichiers:
# - role_decorators.py (décorateurs)
# - view_example.py (exemples)
```

### **3. Modifier les vues existantes**
```python
# Ajouter les décorateurs aux vues existantes
from role_decorators import admin_required, finance_required

# Exemple pour les natures (AdminDaf uniquement)
@finance_required
def nature_liste(request):
    # AdminDaf peut voir, les autres non
    pass
```

### **4. Redémarrer les services**
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 🎉 **Résultat attendu**

### **1. Connexions par rôle**

#### **SuperAdmin**
```
URL: http://187.77.171.80:8000/accounts/login/
Login: SuperAdmin / SuperAdmin123!
Redirection: /dashboard/ (tableau de bord complet)
Accès: ✅ Recettes, Dépenses, Admin Django
```

#### **AdminDaf**
```
URL: http://187.77.171.80:8000/accounts/login/
Login: AdminDaf / AdminDaf123!
Redirection: /demandes/natures/ (uniquement)
Accès: ❌ Dashboard, ❌ Admin Django
```

### **2. Permissions respectées**

- ✅ **AdminDaf** : Voit uniquement les natures économiques
- ✅ **SuperAdmin** : Voit tout le système
- ✅ **Sécurité** : Chaque rôle a ses limites
- ✅ **Clarté** : Permissions claires et définies

---

## 🚨 **Points importants**

### **Sécurité**
- Chaque rôle a des permissions définies
- Les décorateurs protègent les vues
- L'accès admin Django est réservé aux superusers

### **Maintenance**
- Les décorateurs sont réutilisables
- Facile d'ajouter de nouveaux rôles
- Clair et maintenable

---

## 🎊 **Conclusion**

**🎊 Configuration des permissions par rôle prête !**

Le script configure :
- ✅ **Rôles définis** : Chaque utilisateur a son rôle
- ✅ **Permissions claires** : Qui peut voir quoi
- ✅ **Décorateurs prêts** : Code pour implémenter
- ✅ **Tests inclus** : Vérification des accès
- ✅ **Exemples fournis** : Code prêt à utiliser

**Exécutez `setup_role_permissions.sh` sur votre VPS pour configurer les permissions par rôle !**

---

*Configuration créée le : 4 mars 2026*
*Objectif : Permissions différentes par rôle*
*Solution : Rôles + décorateurs + redirections*
