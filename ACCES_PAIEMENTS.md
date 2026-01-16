# 🎯 Guide d'Accès aux Fonctionnalités de Paiement

## 🚀 Étape 1 : Accéder à l'application

L'application est accessible sur : **http://localhost:8001**

## 🔐 Étape 2 : Se connecter

Utilisez les identifiants de test créés automatiquement :

- **Nom d'utilisateur** : `comptable_test`
- **Mot de passe** : `password123`
- **Rôle** : Comptable (peut effectuer des paiements)

## 📍 Étape 3 : Accéder au menu des paiements

Dans le menu latéral gauche, vous trouverez maintenant une nouvelle option :

```
📊 Tableau de bord
🏦 Banques
💳 Comptes bancaires  
📄 Demandes de paiement
💳 **Paiements** ← NOUVEAU
📋 Relevés de dépenses
📝 Dépenses
💰 Recettes
📄 Relevés bancaires
🔄 Rapprochements
📈 Rapports consolidés
```

Cliquez sur **"Paiements"** pour accéder aux nouvelles fonctionnalités.

## 💰 Étape 4 : Tester les fonctionnalités

### Méthode 1 : Payer par relevé (Recommandé)

1. Dans la page des paiements, cliquez sur **"Payer par relevé"**
2. Sélectionnez un relevé bancaire (ex: "BANQUE TEST - Compte Test USD")
3. Vous verrez toutes les demandes à payer pour ce relevé
4. Saisissez les montants pour chaque demande
5. Cliquez sur **"Valider les paiements"**

### Méthode 2 : Paiement individuel

1. Dans la page des paiements, cliquez sur **"Nouveau paiement"**
2. Sélectionnez un relevé bancaire
3. Sélectionnez une demande spécifique
4. Saisissez le montant à payer
5. Ajoutez des observations si nécessaire
6. Cliquez sur **"Effectuer le paiement"**

## 📊 Données de test disponibles

### Demandes créées (USD) :
- DEM-TEST-001 : Achat de matériel informatique (2 500,00 USD)
- DEM-TEST-002 : Frais de formation (1 500,00 USD)
- DEM-TEST-003 : Maintenance véhicules (800,00 USD)

### Demandes créées (CDF) :
- DEM-TEST-004 : Achat fournitures de bureau (50 000 000,00 CDF)

### Relevés bancaires :
- Relevé USD : Période du mois dernier avec 70 000,00 USD de solde
- Relevé CDF : Période du mois dernier avec 200 000 000,00 CDF de solde

## ✅ Ce que vous pouvez tester

1. **Paiement partiel** : Payer une partie d'une demande
2. **Paiement complet** : Payer le reste d'une demande
3. **Paiements multiples** : Payer plusieurs demandes en même temps
4. **Archivage automatique** : Quand un relevé est entièrement payé
5. **Historique** : Voir tous les paiements effectués
6. **Détails** : Consulter les informations de chaque paiement

## 🎯 Résultats attendus

- Les demandes payées partiellement restent avec un "reste à payer"
- Les demandes entièrement payées passent au statut "PAYEE"
- Les relevés avec toutes les demandes payées sont archivés automatiquement
- L'historique des paiements est conservé

## 🔧 Si vous rencontrez des problèmes

1. **Vérifiez que vous êtes bien connecté** avec `comptable_test`
2. **Rafraîchissez la page** si le menu n'apparaît pas
3. **Vérifiez les permissions** : seul un comptable/DAF/DG peut payer
4. **Redémarrez le serveur** si nécessaire : `python manage.py runserver 8001`

---

🎉 **Félicitations !** Vous pouvez maintenant utiliser la fonctionnalité complète de paiement des demandes !
