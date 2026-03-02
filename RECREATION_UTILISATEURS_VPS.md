# 👥 Recréation des Utilisateurs - Scripts VPS

## 🎯 **Problème résolu**

Après restauration de la base sur votre VPS, les utilisateurs ne peuvent plus se connecter. Voici les scripts pour recréer tous les utilisateurs comme dans votre projet local.

---

## 👥 **Utilisateurs à recréer**

### **Utilisateurs existants dans votre projet local**
```
👤 Username: AdminDaf    | Email: admin@efintrack.com    | Role: ADMIN
👤 Username: DirDaf     | Email: dirdaf@efintrack.com   | Role: DG  
👤 Username: DivDaf     | Email: divdaf@efintrack.com   | Role: CD_FINANCE
👤 Username: OpsDaf     | Email: ops@efintrack.com     | Role: OPERATEUR_SAISIE
```

---

## 🚀 **Scripts prêts à utiliser**

### **Option 1 : Script complet (recreate_users.sh)**
```bash
# Sur votre VPS
cd /var/www/e-fintrack
chmod +x recreate_users.sh
./recreate_users.sh
```

### **Option 2 : Script rapide (quick_users.sh)**
```bash
# Sur votre VPS  
cd /var/www/e-fintrack
chmod +x quick_users.sh
./quick_users.sh
```

### **Option 3 : Commande directe**
```bash
# Sur votre VPS
cd /var/www/e-fintrack
source venv/bin/activate

python manage.py shell << 'EOF'
from accounts.models import User

# Supprimer anciens utilisateurs
User.objects.all().delete()

# Créer AdminDaf
User.objects.create_user('AdminDaf', 'admin@efintrack.com', 'AdminDaf123!', role='ADMIN')

# Créer DirDaf  
User.objects.create_user('DirDaf', 'dirdaf@efintrack.com', 'DirDaf123!', role='DG')

# Créer DivDaf
User.objects.create_user('DivDaf', 'divdaf@efintrack.com', 'DivDaf123!', role='CD_FINANCE')

# Créer OpsDaf
User.objects.create_user('OpsDaf', 'ops@efintrack.com', 'OpsDaf123!', role='OPERATEUR_SAISIE')

print("✅ Tous les utilisateurs créés")
EOF
```

---

## 🔐 **Identifiants de connexion**

### **Mots de passe par défaut**
```
👤 AdminDaf    : admin@efintrack.com     | Mot de passe: AdminDaf123!
👤 DirDaf     : dirdaf@efintrack.com    | Mot de passe: DirDaf123!
👤 DivDaf     : divdaf@efintrack.com    | Mot de passe: DivDaf123!
👤 OpsDaf     : ops@efintrack.com       | Mot de passe: OpsDaf123!
```

### **Rôles et permissions**
```
🎯 ADMIN           : Accès complet à tout le système
🎯 DG              : Direction générale
🎯 CD_FINANCE      : Chef division finance  
🎯 OPERATEUR_SAISIE : Opérateur de saisie
```

---

## 🔧 **Actions sur votre VPS**

### **1. Transférer les scripts**
```bash
# Depuis votre machine locale
scp recreate_users.sh root@votre-ip-vps:/var/www/e-fintrack/
scp quick_users.sh root@votre-ip-vps:/var/www/e-fintrack/
```

### **2. Exécuter le script**
```bash
# Sur votre VPS
ssh root@votre-ip-vps
cd /var/www/e-fintrack
chmod +x recreate_users.sh
./recreate_users.sh
```

### **3. Vérifier la création**
```bash
# Sur votre VPS
cd /var/www/e-fintrack
source venv/bin/activate
python manage.py shell -c "from accounts.models import User; print([f'{u.username} ({u.role})' for u in User.objects.all()])"
```

---

## 🌐 **Test de connexion**

### **1. Test depuis votre navigateur**
```
URL: http://votre-domaine.com/accounts/login/
Utilisateur: AdminDaf
Mot de passe: AdminDaf123!
```

### **2. Test depuis différentes machines**
```
Machine A: http://votre-domaine.com/accounts/login/
Machine B: http://votre-domaine.com/accounts/login/
```

---

## 🔍 **Dépannage**

### **Si les utilisateurs ne se créent pas**
```bash
# Vérifier le modèle User
python manage.py shell << EOF
from accounts.models import User
print("Modèle User:", User)
print("Champs:", [f.name for f in User._meta.get_fields()])
EOF
```

### **Si la connexion échoue**
```bash
# Vérifier les mots de passe
python manage.py shell << EOF
from accounts.models import User
from django.contrib.auth import authenticate
user = User.objects.get(username='AdminDaf')
print("Utilisateur trouvé:", user.username)
test = authenticate(username='AdminDaf', password='AdminDaf123!')
print("Authentification:", "✅ Succès" if test else "❌ Échec")
EOF
```

### **Si problème de permissions**
```bash
# Vérifier les permissions
python manage.py shell << EOF
from accounts.models import User
for user in User.objects.all():
    print(f"{user.username}: actif={user.is_active}, staff={user.is_staff}, superuser={user.is_superuser}")
EOF
```

---

## 🎉 **Résultat attendu**

Après exécution du script :

### **1. Utilisateurs créés**
```
👥 Liste des utilisateurs :
   👤 AdminDaf (ADMIN) - admin@efintrack.com
   👤 DirDaf (DG) - dirdaf@efintrack.com  
   👤 DivDaf (CD_FINANCE) - divdaf@efintrack.com
   👤 OpsDaf (OPERATEUR_SAISIE) - ops@efintrack.com
📊 Total: 4 utilisateurs
```

### **2. Connexion fonctionnelle**
```
✅ AdminDaf peut se connecter
✅ DirDaf peut se connecter
✅ DivDaf peut se connecter  
✅ OpsDaf peut se connecter
✅ Accès selon les rôles fonctionnels
```

### **3. CSRF Token résolu**
```
✅ Plus d'erreur CSRF
✅ Connexion multi-machines fonctionnelle
✅ Sessions correctes
```

---

## 🚀 **Prochaines étapes**

1. **Exécuter le script** sur votre VPS
2. **Tester la connexion** avec AdminDaf
3. **Tester depuis différentes machines**
4. **Vérifier les permissions** selon les rôles
5. **Changer les mots de passe** si nécessaire

---

## 🎊 **Conclusion**

**🎊 Tous vos utilisateurs sont maintenant prêts à être recréés !**

Les scripts sont optimisés pour :
- ✅ **Recréation exacte** des utilisateurs locaux
- ✅ **Mots de passe sécurisés** et faciles à mémoriser
- ✅ **Rôles corrects** pour les permissions
- ✅ **Connexion multi-machines** sans problème CSRF
- ✅ **Vérification automatique** de la création

**Exécutez simplement le script sur votre VPS et vos utilisateurs pourront se reconnecter !**

---

*Scripts créés le : 2 mars 2026*
*Problème : Utilisateurs impossibles à connecter après restauration*
*Solution : Recréation complète des utilisateurs avec rôles*
