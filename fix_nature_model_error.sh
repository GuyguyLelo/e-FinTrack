#!/bin/bash
# fix_nature_model_error.sh - Correction du modèle Nature manquant

set -e

echo "🔧 Correction du Modèle Nature Manquant"
echo "===================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Diagnostic du modèle Nature..."
echo "Erreur: cannot import name 'Nature' from 'demandes.models'"

echo ""
echo "🔍 2. Vérification des modèles existants..."
python manage.py shell << 'EOF'
import inspect
from demandes import models

print("🧪 Modèles dans demandes.models:")
for name in dir(models):
    obj = getattr(models, name)
    if inspect.isclass(obj) and hasattr(obj, '_meta'):
        print(f"   ✅ {name}: {obj}")

EOF

echo ""
echo "🔍 3. Vérification du fichier models.py..."
if [ -f "demandes/models.py" ]; then
    echo "📋 Contenu de demandes/models.py:"
    grep -n "class.*models.Model" demandes/models.py || echo "   ❌ Aucun modèle trouvé"
else
    echo "❌ demandes/models.py non trouvé"
fi

echo ""
echo "🔧 4. Création du modèle Nature manquant..."
cat >> demandes/models.py << 'NATURE_MODEL'

class Nature(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    libelle = models.CharField(max_length=200, verbose_name="Libellé")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nature Économique"
        verbose_name_plural = "Natures Économiques"
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.libelle}"

NATURE_MODEL

echo "✅ Modèle Nature créé"

echo ""
echo "🔄 5. Migration du nouveau modèle..."
python manage.py makemigrations demandes
python manage.py migrate

echo ""
echo "🌐 6. Test du modèle Nature..."
python manage.py shell << 'EOF'
from demandes.models import Nature

print("🧪 Test du modèle Nature:")
try:
    # Créer une nature de test
    nature, created = Nature.objects.get_or_create(
        code="TEST001",
        defaults={
            'libelle': 'Nature de test',
            'description': 'Description de test'
        }
    )
    
    if created:
        print("   ✅ Nature de test créée")
    else:
        print("   ✅ Nature de test existante")
    
    print(f"   📋 Nature: {nature}")
    print(f"   📊 Total natures: {Nature.objects.count()}")
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "🔄 7. Redémarrage des services..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo ""
echo "🌐 8. Test final..."
python manage.py shell << 'EOF'
from django.test import Client
from accounts.models import User

print("🧪 Test final:")
try:
    admin_daf = User.objects.get(username='AdminDaf')
    client = Client()
    client.force_login(admin_daf)
    
    response = client.get('/demandes/natures/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Vue des natures fonctionne")
    elif response.status_code == 302:
        print("   ⚠️  Redirection - vérifiez les décorateurs")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "✅ Correction du modèle Nature terminée !"
echo "🎊 Le modèle Nature est maintenant disponible"
