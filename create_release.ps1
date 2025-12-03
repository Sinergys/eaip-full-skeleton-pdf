Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# GitHub repository info
$owner = "Sinergys"
$repo = "eaip-full-skeleton-pdf"
$tag = "v0.2.0"
$title = "EAIP Full Skeleton — Stable Cyrillic PDF Build"

# Release notes
$releaseNotes = @"
✅ Stable release v0.2.0

What's new:

- Added TTF font (DejaVuSans/Arial) for Cyrillic PDF generation
- Improved reports service with full Unicode support
- Added readiness check for reports (port 8005)
- Updated analytics model with optional meterId
- Updated documentation (README, CHANGELOG, PDF_GENERATION.md)
- Cleaned up nested fonts and compose warnings
"@

# Get GitHub token from environment or use gh CLI
$token = $env:GITHUB_TOKEN

if (-not $token) {
    Write-Host "Checking GitHub CLI authentication..."
    try {
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        & gh auth status 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Using GitHub CLI authentication..."
            $token = (& gh auth token)
        }
    } catch {
        Write-Host "GitHub CLI not authenticated. Trying to get token from environment..."
    }
}

if (-not $token) {
    Write-Host ""
    Write-Host "❌ Error: GitHub token not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please either:" -ForegroundColor Yellow
    Write-Host "  1. Set GITHUB_TOKEN environment variable, or" -ForegroundColor Yellow
    Write-Host "  2. Run: gh auth login" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Create release JSON body
$releaseBody = @{
    tag_name = $tag
    name = $title
    body = $releaseNotes
    draft = $false
    prerelease = $false
} | ConvertTo-Json -Depth 10

Write-Host "Creating GitHub release v0.2.0..." -ForegroundColor Cyan
Write-Host "Repository: $owner/$repo" -ForegroundColor Gray
Write-Host "Tag: $tag" -ForegroundColor Gray
Write-Host "Title: $title" -ForegroundColor Gray
Write-Host ""

try {
    $headers = @{
        "Authorization" = "token $token"
        "Accept" = "application/vnd.github.v3+json"
        "User-Agent" = "PowerShell"
    }

    $uri = "https://api.github.com/repos/$owner/$repo/releases"
    
    $response = Invoke-RestMethod -Uri $uri -Method Post -Headers $headers -Body $releaseBody -ContentType "application/json"
    
    Write-Host "✅ Release created successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Release URL: $($response.html_url)" -ForegroundColor Cyan
    Write-Host "Release ID: $($response.id)" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    $errorDetails = $_.ErrorDetails.Message
    if ($errorDetails) {
        try {
            $errorJson = $errorDetails | ConvertFrom-Json
            Write-Host "❌ Error: $($errorJson.message)" -ForegroundColor Red
            if ($errorJson.errors) {
                foreach ($err in $errorJson.errors) {
                    Write-Host "   - $($err.message)" -ForegroundColor Red
                }
            }
        } catch {
            Write-Host "❌ Error: $errorDetails" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Error: $_" -ForegroundColor Red
    }
    exit 1
}

