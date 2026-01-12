# Script de démarrage pour e-Finance DAF
# Usage: .\start.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   e-Finance DAF - Démarrage" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Activer l'environnement virtuel
Write-Host "[1/4] Activation de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
    Write-Host "✓ Environnement virtuel activé" -ForegroundColor Green
} else {
    Write-Host "✗ Environnement virtuel non trouvé. Créez-le avec: python -m venv venv" -ForegroundColor Red
    exit 1
}

# Vérifier la connexion à la base de données
Write-Host ""
Write-Host "[2/4] Vérification de la configuration..." -ForegroundColor Yellow
python manage.py check --deploy
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠ Avertissements détectés (peuvent être ignorés en développement)" -ForegroundColor Yellow
}

# Appliquer les migrations si nécessaire
Write-Host ""
Write-Host "[3/4] Vérification des migrations..." -ForegroundColor Yellow
$migrations = python manage.py showmigrations 2>&1 | Select-String "\[ \]"
if ($migrations) {
    Write-Host "⚠ Des migrations non appliquées ont été détectées" -ForegroundColor Yellow
    Write-Host "  Exécutez: python manage.py migrate" -ForegroundColor Yellow
} else {
    Write-Host "✓ Toutes les migrations sont appliquées" -ForegroundColor Green
}

# Démarrer le serveur
Write-Host ""
Write-Host "[4/4] Démarrage du serveur Django..." -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "   Serveur accessible sur:" -ForegroundColor Green
Write-Host "   http://localhost:8000" -ForegroundColor White
Write-Host ""
Write-Host "   Admin: http://localhost:8000/admin" -ForegroundColor White
Write-Host ""
Write-Host "   Appuyez sur Ctrl+C pour arrêter" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

python manage.py runserver

