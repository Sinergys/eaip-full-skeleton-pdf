Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🔍 Checking GitHub Actions Workflow Configuration" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub token is available
$token = $env:GITHUB_TOKEN
if (-not $token) {
    $token = [System.Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")
}

if (-not $token) {
    Write-Host "⚠️  GitHub token not found in environment" -ForegroundColor Yellow
    Write-Host "   Set GITHUB_TOKEN to check secrets status via API" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✅ GitHub token found" -ForegroundColor Green
}

# Repository info
$owner = "Sinergys"
$repo = "eaip-full-skeleton-pdf"

Write-Host "Repository: $owner/$repo" -ForegroundColor Gray
Write-Host ""

# Check workflow file exists
$workflowPath = ".github/workflows/docker.yml"
if (Test-Path $workflowPath) {
    Write-Host "✅ Workflow file exists: $workflowPath" -ForegroundColor Green
    
    # Check if workflow references secrets
    $workflowContent = Get-Content $workflowPath -Raw
    if ($workflowContent -match "secrets\.DOCKERHUB_USERNAME") {
        Write-Host "✅ Workflow references DOCKERHUB_USERNAME secret" -ForegroundColor Green
    } else {
        Write-Host "❌ Workflow does not reference DOCKERHUB_USERNAME" -ForegroundColor Red
    }
    
    if ($workflowContent -match "secrets\.DOCKERHUB_TOKEN") {
        Write-Host "✅ Workflow references DOCKERHUB_TOKEN secret" -ForegroundColor Green
    } else {
        Write-Host "❌ Workflow does not reference DOCKERHUB_TOKEN" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Workflow file not found: $workflowPath" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 Manual Steps Required:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to: https://github.com/$owner/$repo/settings/secrets/actions" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Add these secrets:" -ForegroundColor Yellow
Write-Host "   - DOCKERHUB_USERNAME (your Docker Hub username)" -ForegroundColor White
Write-Host "   - DOCKERHUB_TOKEN (your Docker Hub access token)" -ForegroundColor White
Write-Host ""
Write-Host "3. Get Docker Hub token:" -ForegroundColor Yellow
Write-Host "   https://hub.docker.com/settings/security" -ForegroundColor White
Write-Host ""
Write-Host "4. After adding secrets, re-run the workflow:" -ForegroundColor Yellow
Write-Host "   https://github.com/$owner/$repo/actions" -ForegroundColor White
Write-Host ""

# Try to check secrets via API if token is available
if ($token) {
    Write-Host "🔐 Attempting to check secrets via GitHub API..." -ForegroundColor Cyan
    try {
        $headers = @{
            "Authorization" = "token $token"
            "Accept" = "application/vnd.github.v3+json"
        }
        
        # Note: GitHub API doesn't allow listing secret names for security reasons
        # We can only check if we have access to the repository
        $repoUrl = "https://api.github.com/repos/$owner/$repo"
        $repoInfo = Invoke-RestMethod -Uri $repoUrl -Headers $headers
        
        Write-Host "✅ Repository access confirmed" -ForegroundColor Green
        Write-Host "   Repository: $($repoInfo.full_name)" -ForegroundColor Gray
        Write-Host "   Visibility: $($repoInfo.visibility)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "ℹ️  Note: GitHub API doesn't allow listing secret names for security." -ForegroundColor Yellow
        Write-Host "   You must verify secrets manually in repository settings." -ForegroundColor Yellow
        
    } catch {
        Write-Host "⚠️  Could not verify repository access via API" -ForegroundColor Yellow
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "✨ Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Add secrets in GitHub (link above)" -ForegroundColor White
Write-Host "   2. Re-run failed workflow or push new commit" -ForegroundColor White
Write-Host "   3. Check Actions tab for build status" -ForegroundColor White
Write-Host ""

