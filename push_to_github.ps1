# Script pour pousser le projet e-Finance_DAF sur GitHub
# Utilisateur: guyguylelo

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Publication sur GitHub - e-Finance_DAF" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que nous sommes dans le bon répertoire
$repoPath = "D:\Developpement\python\projets\e-Finance_DAF"
if (Test-Path $repoPath) {
    Set-Location $repoPath
    Write-Host "✓ Répertoire du projet: $repoPath" -ForegroundColor Green
} else {
    Write-Host "✗ Répertoire non trouvé: $repoPath" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Vérifier que Git est initialisé
if (-not (Test-Path ".git")) {
    Write-Host "✗ Le dépôt Git n'est pas initialisé!" -ForegroundColor Red
    Write-Host "  Exécutez d'abord: git init" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Dépôt Git détecté" -ForegroundColor Green
Write-Host ""

# Vérifier les remotes existants
$existingRemote = git remote get-url origin 2>$null
if ($existingRemote) {
    Write-Host "⚠ Remote 'origin' existe déjà: $existingRemote" -ForegroundColor Yellow
    $response = Read-Host "Voulez-vous le remplacer? (O/N)"
    if ($response -eq "O" -or $response -eq "o") {
        git remote remove origin
        Write-Host "✓ Remote 'origin' supprimé" -ForegroundColor Green
    } else {
        Write-Host "Opération annulée." -ForegroundColor Yellow
        exit 0
    }
}

# Ajouter le remote GitHub
$githubUrl = "https://github.com/guyguylelo/e-Finance_DAF.git"
Write-Host ""
Write-Host "📡 Ajout du remote GitHub..." -ForegroundColor Cyan
Write-Host "   URL: $githubUrl" -ForegroundColor Gray

try {
    git remote add origin $githubUrl
    Write-Host "✓ Remote 'origin' ajouté avec succès" -ForegroundColor Green
} catch {
    Write-Host "✗ Erreur lors de l'ajout du remote: $_" -ForegroundColor Red
    exit 1
}

# Vérifier le remote
Write-Host ""
Write-Host "📋 Vérification des remotes:" -ForegroundColor Cyan
git remote -v

# Renommer la branche en 'main' si nécessaire
Write-Host ""
Write-Host "🌿 Vérification de la branche..." -ForegroundColor Cyan
$currentBranch = git branch --show-current
Write-Host "   Branche actuelle: $currentBranch" -ForegroundColor Gray

if ($currentBranch -ne "main") {
    Write-Host "   Renommage de '$currentBranch' en 'main'..." -ForegroundColor Yellow
    git branch -M main
    Write-Host "✓ Branche renommée en 'main'" -ForegroundColor Green
} else {
    Write-Host "✓ Branche déjà sur 'main'" -ForegroundColor Green
}

# Vérifier qu'il y a un commit
$commitCount = (git rev-list --count HEAD 2>$null)
if ($commitCount -eq 0) {
    Write-Host ""
    Write-Host "⚠ Aucun commit trouvé!" -ForegroundColor Yellow
    Write-Host "   Créez d'abord un commit avec: git commit -m 'Initial commit'" -ForegroundColor Yellow
    exit 1
}

Write-Host "   Commits locaux: $commitCount" -ForegroundColor Gray
Write-Host ""

# Instructions pour l'authentification
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  ⚠ IMPORTANT: Authentification GitHub" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "GitHub vous demandera vos identifiants:" -ForegroundColor White
Write-Host "  • Username: guyguylelo" -ForegroundColor Gray
Write-Host "  • Password: Utilisez un Personal Access Token (PAS votre mot de passe)" -ForegroundColor Gray
Write-Host ""
Write-Host "📝 Créez un token ici si nécessaire:" -ForegroundColor Cyan
Write-Host "   https://github.com/settings/tokens" -ForegroundColor Blue
Write-Host ""
Write-Host "   Scopes nécessaires: repo (toutes les permissions)" -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Prêt à pousser le code? (O/N)"
if ($response -ne "O" -and $response -ne "o") {
    Write-Host "Opération annulée." -ForegroundColor Yellow
    exit 0
}

# Pousser le code
Write-Host ""
Write-Host "📤 Pousse du code sur GitHub..." -ForegroundColor Cyan
Write-Host ""

try {
    git push -u origin main
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Green
    Write-Host "  ✓ Code poussé avec succès!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Votre dépôt est disponible sur:" -ForegroundColor Cyan
    Write-Host "   https://github.com/guyguylelo/e-Finance_DAF" -ForegroundColor Blue
    Write-Host ""
} catch {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "  ✗ Erreur lors du push" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez:" -ForegroundColor Yellow
    Write-Host "  1. Que le dépôt existe sur GitHub" -ForegroundColor Gray
    Write-Host "  2. Que vous utilisez un Personal Access Token valide" -ForegroundColor Gray
    Write-Host "  3. Que vous avez les permissions sur le dépôt" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Vous pouvez réessayer avec: git push -u origin main" -ForegroundColor Yellow
    exit 1
}


