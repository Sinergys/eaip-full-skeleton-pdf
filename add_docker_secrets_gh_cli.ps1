Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🔐 Adding Docker Hub secrets using GitHub CLI" -ForegroundColor Cyan
Write-Host ""

# Docker Hub credentials
$dockerhubUsername = "ecosinergys"
$dockerhubToken = "***REMOVED***"

# Repository
$repo = "Sinergys/eaip-full-skeleton-pdf"

# Check if GitHub CLI is available
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

try {
    $null = & gh --version 2>&1
    Write-Host "✅ GitHub CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   winget install --id GitHub.cli" -ForegroundColor Yellow
    exit 1
}

# Check if authenticated
Write-Host "🔍 Checking GitHub CLI authentication..." -ForegroundColor Cyan
try {
    $authStatus = & gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Not authenticated. Please run: gh auth login" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ GitHub CLI authenticated" -ForegroundColor Green
} catch {
    Write-Host "❌ Authentication check failed. Please run: gh auth login" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📤 Adding secrets to repository: $repo" -ForegroundColor Cyan
Write-Host ""

# Add DOCKERHUB_USERNAME
Write-Host "   Adding DOCKERHUB_USERNAME..." -ForegroundColor Gray
try {
    $dockerhubUsername | & gh secret set DOCKERHUB_USERNAME --repo $repo
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ DOCKERHUB_USERNAME added successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to add DOCKERHUB_USERNAME" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error adding DOCKERHUB_USERNAME: $_" -ForegroundColor Red
    exit 1
}

# Add DOCKERHUB_TOKEN
Write-Host "   Adding DOCKERHUB_TOKEN..." -ForegroundColor Gray
try {
    $dockerhubToken | & gh secret set DOCKERHUB_TOKEN --repo $repo
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ DOCKERHUB_TOKEN added successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to add DOCKERHUB_TOKEN" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error adding DOCKERHUB_TOKEN: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ All secrets added successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "✨ Next steps:" -ForegroundColor Cyan
Write-Host "   1. Re-run the failed workflow:" -ForegroundColor White
Write-Host "      https://github.com/$repo/actions" -ForegroundColor Yellow
Write-Host ""
Write-Host "   2. Or push a new commit to trigger a fresh build" -ForegroundColor White
Write-Host ""

