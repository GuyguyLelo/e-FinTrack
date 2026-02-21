# Guide d'accès Admin Django pour AdminDaf

## 🔐 Connexion à l'admin Django

### 1. Démarrer le serveur
```bash
source venv/bin/activate
python manage.py runserver
```

### 2. Accéder à l'admin
- URL: http://127.0.0.1:8000/admin/
- Username: `AdminDaf`
- Password: [mot de passe actuel de l'utilisateur]

## 📋 Permissions de AdminDaf

L'utilisateur `AdminDaf` (rôle: ADMIN) peut :

### ✅ Utilisateurs
- **Voir** tous les utilisateurs (sauf SUPER_ADMIN)
- **Créer** de nouveaux utilisateurs
- **Modifier** les utilisateurs existants
- **❌ Supprimer** des utilisateurs (réservé au SUPER_ADMIN)

### ✅ Natures Économiques  
- **Voir** toutes les natures économiques
- **Créer** de nouvelles natures économiques
- **Modifier** les natures existantes
- **❌ Supprimer** des natures (sécurité)

### ✅ Services
- **Voir** tous les services
- **Créer** de nouveaux services
- **Modifier** les services existants

### 📊 Autres modèles
- **Voir** tous les autres modèles (lecture seule)
- **❌ Modifier** les autres modèles (protégé)

## 🚀 Comment créer un utilisateur

1. Allez dans `/admin/accounts/user/add/`
2. Remplissez les champs:
   - Username: `nomutilisateur`
   - Email: `email@exemple.com`
   - Password1 et Password2: `motdepasse`
   - Role: choisissez parmi (SUPER_ADMIN, ADMIN, DG, DF, CD_FINANCE, OPERATEUR_SAISIE, AGENT_PAYEUR)
   - Service: sélectionnez un service existant
   - Actif: cochez si l'utilisateur doit être actif

3. Cliquez sur "Save"

## 🌿 Comment ajouter une nature économique

1. Allez dans `/admin/demandes/natureeconomique/add/`
2. Remplissez les champs:
   - Code: `123` (code unique)
   - Titre: `Libellé de la nature économique`
   - Description: optionnel
   - Code parent: si c'est une sous-catégorie
   - Actif: cochez si la nature doit être active

3. Cliquez sur "Save"

## 🔒 Sécurité

- L'utilisateur AdminDaf ne peut pas supprimer de données (sécurité)
- Il ne peut pas modifier les SUPER_ADMIN
- Il ne peut pas accéder aux fonctions système sensibles

## 📞 Support

En cas de problème, vérifiez:
1. Que le serveur Django est bien démarré
2. Que vous utilisez les bons identifiants
3. Que l'utilisateur est bien actif (`is_staff=True`)
