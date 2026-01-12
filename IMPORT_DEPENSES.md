# 📥 Guide d'Importation des Dépenses

Ce guide explique comment importer les données de dépenses dans l'application e-Finance DAF.

## Méthode 1 : Utiliser le script Python (Recommandé)

### Étape 1 : Sauvegarder vos données

Créez un fichier texte (par exemple `depenses.txt`) avec vos données au format tabulaire :

```
CODE DEPENSE	MOIS	ANNEE	DATE	ARTICLE LITTERA	LIBELLE DEPENSES	BANQUE	MONTANT EN Fc	MONTANT EN $us	OBSERVATION
99	2010	2008	16/11/2008	22-10	Frais bancaires	BIC	15 088,46 	569,06 	
100	11	2008	16/11/2008	34-10	Indemnités permanentes	BIC	5 973 000,00 	94 650,00 	
...
```

### Étape 2 : Exécuter le script d'import

```bash
# Option 1 : Lire depuis un fichier
python import_depenses_data.py --file depenses.txt

# Option 2 : Lire depuis stdin (PowerShell)
Get-Content depenses.txt | python import_depenses_data.py

# Option 3 : Utiliser la commande de management Django
python manage.py import_depenses --file depenses.txt --user admin --service "Direction Générale" --statut PAYEE
```

## Méthode 2 : Utiliser la commande de management Django

### Étape 1 : Préparer les données

Sauvegardez vos données dans un fichier texte avec les colonnes séparées par des tabulations.

### Étape 2 : Exécuter la commande

```bash
python manage.py import_depenses --file depenses.txt --user admin --service "Direction Générale" --statut PAYEE
```

### Options disponibles :

- `--file` : Chemin vers le fichier contenant les données
- `--user` : Nom d'utilisateur pour créer les demandes (défaut: admin)
- `--service` : Service demandeur (défaut: Direction Générale)
- `--statut` : Statut des demandes importées (EN_ATTENTE, VALIDEE_DG, VALIDEE_DF, PAYEE, REJETEE) - défaut: PAYEE

## Format des données

Les données doivent être au format tabulaire avec les colonnes suivantes (séparées par des tabulations) :

1. **CODE DEPENSE** : Code unique de la dépense
2. **MOIS** : Mois (1-12)
3. **ANNEE** : Année (ex: 2008)
4. **DATE** : Date au format DD/MM/YYYY (ex: 16/11/2008)
5. **ARTICLE LITTERA** : Code de nomenclature (ex: 22-10, 34-10)
6. **LIBELLE DEPENSES** : Description de la dépense
7. **BANQUE** : Nom de la banque (BIC, TMB, CITI BANK, BCDC, etc.)
8. **MONTANT EN Fc** : Montant en Francs Congolais (format: 15 088,46)
9. **MONTANT EN $us** : Montant en Dollars US (format: 569,06)
10. **OBSERVATION** : Observations supplémentaires (optionnel)

## Comportement de l'import

- **Création automatique** : Les banques et nomenclatures non existantes seront créées automatiquement
- **Double enregistrement** : Si une ligne contient à la fois un montant CDF et USD, deux demandes de paiement seront créées (une pour chaque devise)
- **Statut** : Par défaut, les demandes sont importées avec le statut "PAYEE" (payée)
- **Validation** : Si le statut est "PAYEE", les demandes sont automatiquement approuvées par l'utilisateur spécifié

## Exemple complet

```bash
# 1. Créer le fichier de données
# Copiez vos données dans depenses.txt

# 2. Importer les données
python import_depenses_data.py --file depenses.txt

# 3. Vérifier les résultats
# Le script affichera le nombre de demandes créées et les erreurs éventuelles
```

## Résolution des problèmes

### Erreur : "Utilisateur introuvable"
- Assurez-vous que l'utilisateur spécifié existe (admin ou guy)
- Créez un utilisateur si nécessaire : `python manage.py createsuperuser`

### Erreur : "Format invalide"
- Vérifiez que les colonnes sont bien séparées par des tabulations
- Vérifiez que toutes les colonnes requises sont présentes

### Erreur : "Date invalide"
- Vérifiez le format de la date (DD/MM/YYYY)
- Si la date est absente, le script utilisera la date actuelle

## Notes importantes

- Les montants avec des espaces (ex: "15 088,46") sont automatiquement nettoyés
- Les virgules dans les montants sont converties en points
- Les lignes avec des montants à zéro sont ignorées
- Les nomenclatures non existantes sont créées automatiquement avec le libellé de la dépense

