#!/bin/bash

# Script pour corriger l'erreur 502 Bad Gateway
echo "🔧 CORRECTION 502 BAD GATEWAY - VPS"
echo "=================================="

# 1. Arrêter les services
echo ""
echo "🛑 Arrêt des services..."
sudo systemctl stop gunicorn
sudo systemctl stop nginx
echo "✅ Services arrêtés"

# 2. Vérifier et tuer les processus gunicorn restants
echo ""
echo "🧹 Nettoyage processus gunicorn..."
pkill -f gunicorn
sleep 2
echo "✅ Processus nettoyés"

# 3. Démarrer gunicorn manuellement pour tester
echo ""
echo "🦄 Démarrage Gunicorn manuel..."
cd /home/kandolo/e-FinTrack
source venv/bin/activate

# Démarrer gunicorn en arrière-plan
nohup gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    efinance_daf.wsgi:application > gunicorn.log 2>&1 &

GUNICORN_PID=$!
echo "✅ Gunicorn démarré (PID: $GUNICORN_PID)"

# 4. Attendre que gunicorn démarre
echo ""
echo "⏳ Attente démarrage Gunicorn..."
sleep 5

# 5. Tester gunicorn localement
echo ""
echo "🌍 Test Gunicorn local..."
if curl -s http://127.0.0.1:8000 > /dev/null; then
    echo "✅ Gunicorn répond localement"
else
    echo "❌ Gunicorn ne répond pas"
    echo "📋 Logs Gunicorn:"
    tail -10 gunicorn.log
    exit 1
fi

# 6. Créer la configuration nginx correcte
echo ""
echo "📝 Configuration nginx pour Gunicorn..."

cat > /tmp/e-fintrack-fixed.conf << 'EOF'
server {
    listen 80;
    server_name 187.77.171.80 localhost;
    
    # Logs
    access_log /var/log/nginx/e-fintrack-access.log;
    error_log /var/log/nginx/e-fintrack-error.log;
    
    # Servir les fichiers statiques
    location /static/ {
        alias /home/kandolo/e-FinTrack/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Servir les fichiers media
    location /media/ {
        alias /home/kandolo/e-FinTrack/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Application Django via Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# 7. Appliquer la configuration nginx
echo ""
echo "🔄 Application configuration nginx..."
sudo cp /tmp/e-fintrack-fixed.conf /etc/nginx/sites-available/e-fintrack
sudo ln -sf /etc/nginx/sites-available/e-fintrack /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default  # Désactiver default

# 8. Tester la configuration nginx
echo ""
echo "🧪 Test configuration nginx..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Configuration nginx valide"
    
    # 9. Démarrer nginx
    echo ""
    echo "🌐 Démarrage nginx..."
    sudo systemctl start nginx
    sleep 3
    
    # 10. Test final
    echo ""
    echo "🌍 Test final..."
    if curl -s http://localhost/ > /dev/null; then
        echo "✅ Site accessible via nginx"
    else
        echo "❌ Site non accessible via nginx"
    fi
    
    # 11. Test admin
    echo ""
    echo "🔧 Test admin..."
    if curl -s http://localhost/admin/ > /dev/null; then
        echo "✅ Admin accessible"
    else
        echo "❌ Admin non accessible"
    fi
    
    # 12. Test fichiers statiques
    echo ""
    echo "📁 Test fichiers statiques..."
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/static/admin/css/base.css)
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ Fichiers statiques accessibles (HTTP $HTTP_STATUS)"
    else
        echo "❌ Fichiers statiques non accessibles (HTTP $HTTP_STATUS)"
    fi
    
else
    echo "❌ Configuration nginx invalide"
    exit 1
fi

# 13. Créer le service systemd pour gunicorn
echo ""
echo "🔧 Création service systemd pour gunicorn..."

cat > /tmp/gunicorn.service << 'EOF'
[Unit]
Description=gunicorn daemon for e-FinTrack
After=network.target

[Service]
User=kandolo
Group=www-data
WorkingDirectory=/home/kandolo/e-FinTrack
Environment="PATH=/home/kandolo/e-FinTrack/venv/bin"
ExecStart=/home/kandolo/e-FinTrack/venv/bin/gunicorn \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    efinance_daf.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn

# 14. Arrêter gunicorn manuel et démarrer le service
echo ""
echo "🔄 Basculement vers service systemd..."
kill $GUNICORN_PID
sleep 2
sudo systemctl start gunicorn
sleep 3

# 15. Vérification finale
echo ""
echo "🔍 Vérification finale:"
sudo systemctl status gunicorn --no-pager
sudo systemctl status nginx --no-pager

echo ""
echo "🌐 ACCÈS:"
echo "   Site: http://187.77.171.80/"
echo "   Admin: http://187.77.171.80/admin/"
echo "   Health: http://187.77.171.80/health"

echo ""
echo "✅ CORRECTION 502 TERMINÉE"
