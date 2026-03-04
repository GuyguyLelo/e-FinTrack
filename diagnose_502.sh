#!/bin/bash

# Script pour diagnostiquer et corriger l'erreur 502 Bad Gateway
echo "🔍 DIAGNOSTIC 502 BAD GATEWAY - VPS"
echo "====================================="

# 1. Vérifier gunicorn
echo ""
echo "🦄 Vérification Gunicorn:"
sudo systemctl status gunicorn
echo ""

# 2. Vérifier les processus gunicorn
echo "🔍 Processus Gunicorn:"
ps aux | grep gunicorn
echo ""

# 3. Vérifier les ports
echo "🔌 Vérification ports:"
netstat -tlnp | grep :8000
echo ""

# 4. Vérifier nginx
echo "🌐 Vérification Nginx:"
sudo systemctl status nginx
echo ""

# 5. Vérifier les logs gunicorn
echo "📋 Logs Gunicorn récents:"
sudo journalctl -u gunicorn --no-pager -n 20
echo ""

# 6. Vérifier les logs nginx
echo "📋 Logs Nginx récents:"
sudo tail -20 /var/log/nginx/error.log
echo ""

# 7. Tester la connexion locale
echo "🌍 Test connexion locale à gunicorn:"
curl -I http://127.0.0.1:8000 || echo "❌ Gunicorn ne répond pas localement"
echo ""

# 8. Vérifier la configuration nginx
echo "⚙️  Configuration nginx actuelle:"
sudo nginx -t
echo ""

# 9. Vérifier le fichier socket gunicorn
echo "🔌 Vérification socket gunicorn:"
if [ -S "/run/gunicorn.sock" ]; then
    echo "✅ Socket gunicorn trouvé: /run/gunicorn.sock"
    ls -la /run/gunicorn.sock
else
    echo "❌ Socket gunicorn non trouvé"
fi

echo ""
echo "🔧 SOLUTIONS POSSIBLES:"
echo "1. Redémarrer gunicorn: sudo systemctl restart gunicorn"
echo "2. Vérifier la configuration gunicorn"
echo "3. Vérifier que gunicorn écoute sur le bon port"
echo "4. Corriger la configuration nginx"
