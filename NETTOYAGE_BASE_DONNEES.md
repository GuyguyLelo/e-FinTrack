# 🗑️ Nettoyage Complet de la Base de Données

## 📋 **Objectif**

Supprimer toutes les données de test (recettes, dépenses, clôtures) pour permettre des tests propres sur une base vide.

---

## 🗑️ **Opérations de nettoyage**

### **1. Suppression des recettes**
```python
from recettes.models import RecetteFeuille

# Supprimer toutes les recettes
nb_recettes = RecetteFeuille.objects.count()
print(f'Recettes à supprimer: {nb_recettes}')
RecetteFeuille.objects.all().delete()
print('✅ Recettes supprimées')
```

**Résultat :** 2 recettes supprimées

### **2. Suppression des dépenses**
```python
from demandes.models import DepenseFeuille

# Supprimer toutes les dépenses
nb_depenses = DepenseFeuille.objects.count()
print(f'Dépenses à supprimer: {nb_depenses}')
DepenseFeuille.objects.all().delete()
print('✅ Dépenses supprimées')
```

**Résultat :** 1 dépense supprimée

### **3. Suppression des clôtures**
```python
from clotures.models import ClotureMensuelle

# Supprimer toutes les clôtures
nb_clotures = ClotureMensuelle.objects.count()
print(f'Clôtures à supprimer: {nb_clotures}')
ClotureMensuelle.objects.all().delete()
print('✅ Clôtures supprimées')
```

**Résultat :** 1 clôture supprimée

---

## 🔍 **Vérification du nettoyage**

### **Contrôle de la base vide**
```python
# Vérification finale
nb_recettes = RecetteFeuille.objects.count()
nb_depenses = DepenseFeuille.objects.count()
nb_clotures = ClotureMensuelle.objects.count()

print(f'Recettes restantes: {nb_recettes}')
print(f'Dépenses restantes: {nb_depenses}')
print(f'Clôtures restantes: {nb_clotures}')

if nb_recettes == 0 and nb_depenses == 0 and nb_clotures == 0:
    print('✅ BASE DE DONNÉES VIDE - PRÊTE POUR LES TESTS')
```

**Résultat :** Base de données complètement vide

---

## 💾 **Données conservées**

### **Références préservées**
Pour ne pas casser l'application, certaines données de référence sont conservées :

#### **1. Natures Économiques**
```python
from demandes.models import NatureEconomique

nb_natures = NatureEconomique.objects.count()
print(f'Natures économiques conservées: {nb_natures}')
# Résultat : 7 natures économiques conservées
```

#### **2. Sources de Recettes**
```python
from recettes.models import SourceRecette

nb_sources = SourceRecette.objects.count()
print(f'Sources de recettes conservées: {nb_sources}')
# Résultat : 4 sources de recettes conservées
```

#### **3. Utilisateurs et Banques**
```python
from accounts.models import User
from banques.models import Banque

# Ces données sont essentielles au fonctionnement
# et ne doivent pas être supprimées
```

---

## 🧪 **Scénarios de test possibles**

### **1. Test de création de période**
```bash
# Créer la période actuelle
python manage.py shell -c "
from clotures.models import ClotureMensuelle
cloture = ClotureMensuelle.get_periode_actuelle()
print(f'Période créée: {cloture.mois:02d}/{cloture.annee} - {cloture.statut}')
"
```

### **2. Test d'ajout de recettes**
```bash
# Ajouter une recette de test
python manage.py shell -c "
from recettes.models import RecetteFeuille
from banques.models import Banque
from django.utils import timezone

recette = RecetteFeuille.objects.create(
    mois=2,
    annee=2026,
    date=timezone.now().date(),
    libelle_recette='Test recette',
    montant_fc=1000000,
    montant_usd=500,
    banque=Banque.objects.first()
)
print(f'Recette créée: {recette.libelle_recette}')
"
```

### **3. Test d'ajout de dépenses**
```bash
# Ajouter une dépense de test
python manage.py shell -c "
from demandes.models import DepenseFeuille
from banques.models import Banque
from django.utils import timezone

depense = DepenseFeuille.objects.create(
    mois=2,
    annee=2026,
    date=timezone.now().date(),
    libelle_depenses='Test dépense',
    montant_fc=500000,
    montant_usd=250,
    banque=Banque.objects.first()
)
print(f'Dépense créée: {depense.libelle_depenses}')
"
```

### **4. Test de clôture**
```bash
# Simuler une clôture (seulement en fin de mois)
python manage.py shell -c "
from clotures.models import ClotureMensuelle
from accounts.models import User

cloture = ClotureMensuelle.get_periode_actuelle()
peut_cloturer, message = cloture.peut_etre_cloture()
print(f'Peut clôturer: {peut_cloturer}')
print(f'Message: {message}')
"
```

---

## 🌐 **Points de contrôle**

### **1. Dashboard vide**
- **URL** : http://127.0.0.1:8001/tableau-bord-feuilles/
- **Attendu** : Tous les soldes à 0.00
- **Vérification** : Cartes affichent correctement les valeurs nulles

### **2. Période actuelle vide**
- **URL** : http://127.0.0.1:8001/clotures/periode-actuelle/
- **Attendu** : Période 02/2026 avec soldes à 0
- **Vérification** : Bouton de clôture désactivé (nous sommes le 22)

### **3. Liste des clôtures vide**
- **URL** : http://127.0.0.1:8001/clotures/
- **Attendu** : Message "Aucune clôture trouvée"
- **Vérification** : Lien vers période actuelle fonctionnel

---

## 🔧 **Commandes de maintenance**

### **1. Nettoyage complet**
```bash
# Script de nettoyage
source venv/bin/activate && python manage.py shell -c "
from recettes.models import RecetteFeuille
from demandes.models import DepenseFeuille
from clotures.models import ClotureMensuelle

print('🗑️ NETTOYAGE COMPLET')
RecetteFeuille.objects.all().delete()
DepenseFeuille.objects.all().delete()
ClotureMensuelle.objects.all().delete()
print('✅ BASE DE DONNÉES VIDÉE')
"
```

### **2. Vérification de l'état**
```bash
# Vérifier l'état de la base
source venv/bin/activate && python manage.py shell -c "
from recettes.models import RecetteFeuille
from demandes.models import DepenseFeuille
from clotures.models import ClotureMensuelle

print('📊 ÉTAT ACTUEL:')
print(f'Recettes: {RecetteFeuille.objects.count()}')
print(f'Dépenses: {DepenseFeuille.objects.count()}')
print(f'Clôtures: {ClotureMensuelle.objects.count()}')
"
```

### **3. Création de données de test**
```bash
# Créer un jeu de test complet
source venv/bin/activate && python manage.py shell -c "
# Créer période, recettes et dépenses de test
# Voir scénarios ci-dessus
"
```

---

## 🎯 **Résultats obtenus**

### ✅ **Base de données propre**
- **Recettes** : 0/0 (supprimé/vérifié)
- **Dépenses** : 0/0 (supprimé/vérifié)
- **Clôtures** : 0/0 (supprimé/vérifié)
- **Références** : Conservées (natures, sources, utilisateurs)

### ✅ **Environnement de test prêt**
- **Dashboard** : Fonctionnel avec soldes à 0
- **Périodes** : Création automatique fonctionnelle
- **Clôtures** : Validation stricte opérationnelle
- **Interface** : Prête pour les tests

---

## 🚀 **Prochaines étapes**

1. **Tests unitaires** : Vérifier toutes les fonctionnalités
2. **Tests d'intégration** : Valider les workflows complets
3. **Tests de charge** : Vérifier les performances
4. **Tests de sécurité** : Valider les permissions

---

## 📞 **En cas de problème**

### **Restauration des données**
```bash
# Si besoin de restaurer les données de référence
python manage.py migrate
# Les natures économiques et sources seront recréées
```

### **Recréation manuelle**
```bash
# Recréer les données essentielles
python manage.py shell -c "
from recettes.models import SourceRecette
from demandes.models import NatureEconomique

# Recréer les sources par défaut
SourceRecette.objects.get_or_create(
    code='BANQUE',
    defaults={'nom': 'Banque', 'description': 'Versements bancaires'}
)
# etc...
"
```

---

## 🎉 **Conclusion**

### ✅ **Nettoyage réussi**
La base de données est maintenant **complètement propre** et **prête pour les tests** :

- 🗑️ **Données de test supprimées** : Recettes, dépenses, clôtures
- 💾 **Références conservées** : Natures, sources, utilisateurs
- 🧪 **Tests possibles** : Tous les scénarios sont faisables
- 🔍 **Vérification validée** : Base bien vide

**🎊 L'environnement est prêt pour des tests complets et propres !**

---

*Nettoyage effectué le : 23 février 2026*
*Opération : Suppression des données de test*
*Statut : ✅ Terminé et vérifié*
*Base : Prête pour les tests*
