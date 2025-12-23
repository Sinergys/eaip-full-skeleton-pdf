Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🔐 GitHub Secrets Setup Script" -ForegroundColor Cyan
Write-Host ""

# Repository info
$owner = "Sinergys"
$repo = "eaip-full-skeleton-pdf"

# Get GitHub token
$token = $env:GITHUB_TOKEN
if (-not $token) {
    $token = [System.Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")
}

if (-not $token) {
    Write-Host "❌ GitHub token not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set GITHUB_TOKEN environment variable:" -ForegroundColor Yellow
    Write-Host '  $env:GITHUB_TOKEN = "your_github_token"' -ForegroundColor White
    Write-Host ""
    Write-Host "Or set it permanently:" -ForegroundColor Yellow
    Write-Host '  [System.Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "your_token", "User")' -ForegroundColor White
    exit 1
}

Write-Host "✅ GitHub token found" -ForegroundColor Green
Write-Host ""

# Get Docker Hub credentials
Write-Host "📝 Enter Docker Hub credentials:" -ForegroundColor Cyan
$dockerhubUsername = Read-Host "Docker Hub Username"
$dockerhubToken = Read-Host "Docker Hub Token (Access Token)" -AsSecureString
$dockerhubTokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($dockerhubToken)
)

if ([string]::IsNullOrWhiteSpace($dockerhubUsername) -or [string]::IsNullOrWhiteSpace($dockerhubTokenPlain)) {
    Write-Host "❌ Docker Hub credentials are required!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Setting up GitHub secrets..." -ForegroundColor Cyan

# GitHub API endpoint for secrets
$baseUrl = "https://api.github.com/repos/$owner/$repo/actions/secrets"

# Function to get public key for encryption
function Get-PublicKey {
    $headers = @{
        "Authorization" = "token $token"
        "Accept" = "application/vnd.github.v3+json"
    }
    
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/public-key" -Headers $headers -Method Get
        return $response
    } catch {
        Write-Host "❌ Failed to get public key: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response.StatusCode -eq 403) {
            Write-Host "   Make sure your token has 'repo' scope and admin access to the repository" -ForegroundColor Yellow
        }
        throw
    }
}

# Function to encrypt secret using public key
function Encrypt-Secret {
    param(
        [string]$Secret,
        [string]$PublicKey,
        [string]$KeyId
    )
    
    # Load System.Security.Cryptography
    Add-Type -AssemblyName System.Security
    
    # Convert public key from base64
    $publicKeyBytes = [Convert]::FromBase64String($PublicKey)
    
    # Import RSA public key
    $rsa = New-Object System.Security.Cryptography.RSACryptoServiceProvider
    $rsa.ImportRSAPublicKey($publicKeyBytes, [ref]$null)
    
    # Encrypt the secret
    $secretBytes = [System.Text.Encoding]::UTF8.GetBytes($Secret)
    $encryptedBytes = $rsa.Encrypt($secretBytes, $false)
    $encryptedSecret = [Convert]::ToBase64String($encryptedBytes)
    
    return $encryptedSecret
}

# Function to set secret
function Set-GitHubSecret {
    param(
        [string]$SecretName,
        [string]$SecretValue,
        [string]$PublicKey,
        [string]$KeyId
    )
    
    $encryptedValue = Encrypt-Secret -Secret $SecretValue -PublicKey $PublicKey -KeyId $KeyId
    
    $headers = @{
        "Authorization" = "token $token"
        "Accept" = "application/vnd.github.v3+json"
    }
    
    $body = @{
        encrypted_value = $encryptedValue
        key_id = $KeyId
    } | ConvertTo-Json
    
    try {
        Invoke-RestMethod -Uri "$baseUrl/$SecretName" -Headers $headers -Method Put -Body $body -ContentType "application/json" | Out-Null
        Write-Host "✅ Secret '$SecretName' set successfully" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "❌ Failed to set secret '$SecretName': $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response.StatusCode -eq 403) {
            Write-Host "   Make sure your token has 'repo' scope and admin access" -ForegroundColor Yellow
        }
        return $false
    }
}

# Get public key
Write-Host "   Getting repository public key..." -ForegroundColor Gray
try {
    $publicKeyInfo = Get-PublicKey
    Write-Host "   ✅ Public key retrieved" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Failed to get public key" -ForegroundColor Red
    exit 1
}

# Set secrets
Write-Host ""
Write-Host "   Setting DOCKERHUB_USERNAME..." -ForegroundColor Gray
$success1 = Set-GitHubSecret -SecretName "DOCKERHUB_USERNAME" -SecretValue $dockerhubUsername -PublicKey $publicKeyInfo.key -KeyId $publicKeyInfo.key_id

Write-Host "   Setting DOCKERHUB_TOKEN..." -ForegroundColor Gray
$success2 = Set-GitHubSecret -SecretName "DOCKERHUB_TOKEN" -SecretValue $dockerhubTokenPlain -PublicKey $publicKeyInfo.key -KeyId $publicKeyInfo.key_id

Write-Host ""

if ($success1 -and $success2) {
    Write-Host "✅ All secrets set successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✨ Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Re-run the failed workflow:" -ForegroundColor White
    Write-Host "      https://github.com/$owner/$repo/actions" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   2. Or push a new commit to trigger a fresh build" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️  Some secrets failed to set. Please check the errors above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can also set them manually:" -ForegroundColor Yellow
    Write-Host "   https://github.com/$owner/$repo/settings/secrets/actions" -ForegroundColor White
    exit 1
}

