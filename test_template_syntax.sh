#!/bin/bash
# test_template_syntax.sh - Test de syntaxe du template corrigé

set -e

echo "🧪 Test de Syntaxe du Template Corrigé"
echo "=================================="

cd ~/e-FinTrack
source venv/bin/activate

echo "🔍 1. Test de syntaxe du template..."

python manage.py shell << 'EOF'
from django.template import Template, Context

print("🧪 Test de syntaxe du template corrigé:")
try:
    with open('templates/base.html', 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    print("   ✅ Syntaxe du template correcte")
    
    # Compter les blocks
    if_count = template_content.count('{% if ')
    endif_count = template_content.count('{% endif %}')
    block_count = template_content.count('{% block ')
    endblock_count = template_content.count('{% endblock %}')
    
    print(f"   📊 Blocks if/endif: {if_count}/{endif_count}")
    print(f"   📊 Blocks block/endblock: {block_count}/{endblock_count}")
    
    if if_count == endif_count and block_count == endblock_count:
        print("   ✅ Toutes les balises sont correctement fermées")
    else:
        print("   ❌ Déséquilibre des balises détecté")
    
except Exception as e:
    print(f"   ❌ Erreur de syntaxe: {e}")

EOF

echo ""
echo "🌐 2. Test du template de login..."

python manage.py shell << 'EOF'
from django.test import Client

print("🧪 Test du template de login:")
try:
    client = Client()
    response = client.get('/accounts/login/')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        if 'form-control' in content:
            print("   ✅ Template de login fonctionne")
        else:
            print("   ❌ Template de login cassé")
    else:
        print(f"   ❌ Erreur: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ Erreur: {e}")

EOF

echo ""
echo "✅ Test de syntaxe terminé !"
