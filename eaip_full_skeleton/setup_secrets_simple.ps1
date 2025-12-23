Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🔐 Simple GitHub Secrets Setup" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is available
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$ghAvailable = $false
try {
    $null = & gh --version 2>&1
    $ghAvailable = $true
} catch {
    $ghAvailable = $false
}

if ($ghAvailable) {
    Write-Host "✅ GitHub CLI (gh) is available" -ForegroundColor Green
    Write-Host ""
    Write-Host "Using GitHub CLI to set secrets..." -ForegroundColor Cyan
    Write-Host ""
    
    # Get credentials
    $dockerhubUsername = Read-Host "Docker Hub Username"
    $dockerhubToken = Read-Host "Docker Hub Token" -AsSecureString
    $dockerhubTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dockerhubToken)
    )
    
    if ([string]::IsNullOrWhiteSpace($dockerhubUsername) -or [string]::IsNullOrWhiteSpace($dockerhubTokenPlain)) {
        Write-Host "❌ Credentials are required!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "Setting secrets via GitHub CLI..." -ForegroundColor Cyan
    
    # Set secrets using gh CLI
    try {
        & gh secret set DOCKERHUB_USERNAME --body $dockerhubUsername --repo Sinergys/eaip-full-skeleton-pdf
        Write-Host "✅ DOCKERHUB_USERNAME set" -ForegroundColor Green
        
        & gh secret set DOCKERHUB_TOKEN --body $dockerhubTokenPlain --repo Sinergys/eaip-full-skeleton-pdf
        Write-Host "✅ DOCKERHUB_TOKEN set" -ForegroundColor Green
        
        Write-Host ""
        Write-Host "✅ All secrets configured successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "✨ Next steps:" -ForegroundColor Cyan
        Write-Host "   1. Re-run the failed workflow:" -ForegroundColor White
        Write-Host "      https://github.com/Sinergys/eaip-full-skeleton-pdf/actions" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "   2. Or push a new commit to trigger a fresh build" -ForegroundColor White
        
    } catch {
        Write-Host "❌ Failed to set secrets: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Make sure you're authenticated:" -ForegroundColor Yellow
        Write-Host "   gh auth login" -ForegroundColor White
        exit 1
    }
    
} else {
    Write-Host "⚠️  GitHub CLI (gh) is not available" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📋 Manual Setup Required:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Option 1: Install GitHub CLI and use this script" -ForegroundColor Yellow
    Write-Host "   winget install --id GitHub.cli" -ForegroundColor White
    Write-Host "   gh auth login" -ForegroundColor White
    Write-Host "   Then run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 2: Set secrets manually via web interface" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://github.com/Sinergys/eaip-full-skeleton-pdf/settings/secrets/actions" -ForegroundColor White
    Write-Host "   2. Click 'New repository secret'" -ForegroundColor White
    Write-Host "   3. Add DOCKERHUB_USERNAME and DOCKERHUB_TOKEN" -ForegroundColor White
    Write-Host ""
    Write-Host "Option 3: Use the API script (requires GitHub token with admin rights)" -ForegroundColor Yellow
    Write-Host "   Run: pwsh -ExecutionPolicy Bypass -File .\setup_github_secrets.ps1" -ForegroundColor White
    Write-Host ""
}

