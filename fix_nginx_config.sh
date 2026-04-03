#!/bin/bash

# Script pour corriger la configuration nginx
echo "🔧 CORRECTION CONFIGURATION NGINX - VPS"
echo "======================================="

# 1. Trouver le fichier de configuration nginx actif
echo ""
echo "🔍 Recherche configuration nginx active..."

CONFIG_FILES=(
    "/etc/nginx/sites-available/e-fintrack"
    "/etc/nginx/sites-available/default"
    "/etc/nginx/conf.d/e-fintrack.conf"
    "/etc/nginx/nginx.conf"
)

ACTIVE_CONFIG=""
for config in "${CONFIG_FILES[@]}"; do
    if [ -f "$config" ]; then
        echo "✅ Configuration trouvée: $config"
        ACTIVE_CONFIG="$config"
        break
    fi
done

if [ -z "$ACTIVE_CONFIG" ]; then
    echo "❌ Aucune configuration trouvée, utilisation de default"
    ACTIVE_CONFIG="/etc/nginx/sites-available/default"
fi

# 2. Créer une sauvegarde
echo ""
echo "💾 Sauvegarde configuration actuelle..."
sudo cp "$ACTIVE_CONFIG" "$ACTIVE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
echo "✅ Sauvegarde créée"

# 3. Créer la configuration correcte
echo ""
echo "📝 Création configuration correcte..."

cat > /tmp/e-fintrack-nginx.conf << 'EOF'
# Configuration e-FinTrack avec fichiers statiques
server {
    listen 80;
    server_name 187.77.171.80 localhost;
    
    # Logs
    access_log /var/log/nginx/e-fintrack-access.log;
    error_log /var/log/nginx/e-fintrack-error.log;
    
    # Servir les fichiers statiques - PRIORITÉ HAUTE
    location /static/ {
        alias /home/kandolo/e-FinTrack/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        add_header X-Content-Type-Options nosniff;
        
        # Forcer le type MIME pour CSS
        location ~* \.css$ {
            add_header Content-Type text/css;
        }
        
        # Forcer le type MIME pour JS
        location ~* \.js$ {
            add_header Content-Type application/javascript;
        }
    }
    
    # Servir les fichiers media
    location /media/ {
        alias /home/kandolo/e-FinTrack/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Application Django via gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Headers pour Django
        proxy_set_header X-Forwarded-Host $server_name;
        proxy_set_header X-Forwarded-Port $server_port;
    }
    
    # Sécurité
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Pages d'erreur
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
EOF

# 4. Appliquer la configuration
echo ""
echo "🔄 Application de la configuration..."
sudo cp /tmp/e-fintrack-nginx.conf "$ACTIVE_CONFIG"
echo "✅ Configuration appliquée"

# 5. Tester la configuration
echo ""
echo "🧪 Test configuration nginx..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Configuration nginx valide"
    
    # 6. Recharger nginx
    echo ""
    echo "🔄 Rechargement nginx..."
    sudo systemctl reload nginx
    echo "✅ Nginx rechargé"
    
    # 7. Vérifier que les fichiers sont accessibles
    echo ""
    echo "🌍 Test accès fichiers statiques..."
    sleep 2
    
    # Test CSS
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/css/base.css)
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ Fichiers CSS accessibles (HTTP $HTTP_STATUS)"
    else
        echo "❌ Fichiers CSS non accessibles (HTTP $HTTP_STATUS)"
    fi
    
    # Test JS
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/js/core.js)
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ Fichiers JS accessibles (HTTP $HTTP_STATUS)"
    else
        echo "❌ Fichiers JS non accessibles (HTTP $HTTP_STATUS)"
    fi
    
else
    echo "❌ Configuration nginx invalide"
    echo "Restauration de la sauvegarde..."
    sudo cp "$ACTIVE_CONFIG.backup.$(date +%Y%m%d_%H%M%S)" "$ACTIVE_CONFIG"
    sudo nginx -t
fi

# 8. Afficher la configuration appliquée
echo ""
echo "📋 Configuration appliquée dans: $ACTIVE_CONFIG"
echo ""
echo "🔍 Vérification manuelle:"
echo "   curl -I http://localhost/static/admin/css/base.css"
echo "   curl -I http://localhost/static/admin/js/core.js"
echo ""
echo "🌐 Test admin: http://187.77.171.80:8000/admin/"

echo ""
echo "✅ CORRECTION NGINX TERMINÉE"
