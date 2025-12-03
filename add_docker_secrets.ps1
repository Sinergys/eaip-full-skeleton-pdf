Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "🔐 Adding Docker Hub secrets to GitHub repository" -ForegroundColor Cyan
Write-Host ""

# Repository info
$owner = "Sinergys"
$repo = "eaip-full-skeleton-pdf"

# Docker Hub credentials
$dockerhubUsername = "ecosinergys"
$dockerhubToken = "***REMOVED***"

# Get GitHub token from environment
$githubToken = [System.Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")
if (-not $githubToken) {
    Write-Host "❌ GitHub token not found in environment!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ GitHub token found" -ForegroundColor Green
Write-Host "Repository: $owner/$repo" -ForegroundColor Gray
Write-Host ""

# GitHub API base URL
$baseUrl = "https://api.github.com/repos/$owner/$repo/actions/secrets"

# Headers for API requests
$headers = @{
    "Authorization" = "token $githubToken"
    "Accept" = "application/vnd.github.v3+json"
}

# Step 1: Get public key
Write-Host "📥 Getting repository public key..." -ForegroundColor Cyan
try {
    $publicKeyResponse = Invoke-RestMethod -Uri "$baseUrl/public-key" -Headers $headers -Method Get
    $publicKey = $publicKeyResponse.key
    $keyId = $publicKeyResponse.key_id
    Write-Host "✅ Public key retrieved (Key ID: $keyId)" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to get public key: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "   Make sure your GitHub token has 'repo' scope and admin access" -ForegroundColor Yellow
    }
    exit 1
}

# Step 2: Encrypt secrets using public key
Write-Host ""
Write-Host "🔒 Encrypting secrets..." -ForegroundColor Cyan

# Function to encrypt using RSA public key
function Encrypt-GitHubSecret {
    param(
        [string]$PlainText,
        [string]$PublicKeyBase64
    )
    
    # Convert base64 public key to bytes
    $publicKeyBytes = [Convert]::FromBase64String($PublicKeyBase64)
    
    # Create RSA parameters from the public key
    # GitHub provides the key in PKCS#1 format (raw modulus + exponent)
    # We need to construct the proper ASN.1 structure
    
    Add-Type -AssemblyName System.Security
    
    # Try using RSACng (more modern, better support)
    try {
        $rsa = New-Object System.Security.Cryptography.RSACng
        
        # GitHub's public key is in PKCS#1 SubjectPublicKeyInfo format
        # We need to construct the proper XML or use ImportRSAPublicKey
        $rsaParameters = New-Object System.Security.Cryptography.RSAParameters
        
        # Parse the key - GitHub provides it as base64 encoded DER
        # The key structure: SEQUENCE { modulus INTEGER, publicExponent INTEGER }
        # For simplicity, let's use a different approach with BouncyCastle or direct byte manipulation
        
        # Alternative: Use the key directly with proper ASN.1 parsing
        # Since PowerShell's RSA support is limited, we'll use a workaround
        
        # Create a temporary file with the key
        $tempKeyFile = [System.IO.Path]::GetTempFileName()
        try {
            # Write the key in PEM format
            $pemKey = "-----BEGIN PUBLIC KEY-----`n"
            $pemKey += ($PublicKeyBase64 -replace '(.{64})', '$1`n')
            $pemKey += "`n-----END PUBLIC KEY-----"
            [System.IO.File]::WriteAllText($tempKeyFile, $pemKey)
            
            # Use openssl if available, or try direct import
            # For now, let's use a simpler approach with RSACryptoServiceProvider
            $rsa = New-Object System.Security.Cryptography.RSACryptoServiceProvider
            
            # Try to import using the raw bytes
            # GitHub's key format: 30 81 9F 30 0D 06 09 2A 86 48 86 F7 0D 01 01 01 05 00 03 81 8D 00 [modulus] [exponent]
            # We need to extract modulus and exponent
            
            # Parse ASN.1 structure manually
            $reader = New-Object System.IO.BinaryReader([System.IO.MemoryStream]$publicKeyBytes)
            
            # Skip ASN.1 header (SEQUENCE)
            if ($publicKeyBytes[0] -eq 0x30) {
                # This is a DER-encoded SubjectPublicKeyInfo
                # We need to extract the actual RSA public key (modulus + exponent)
                
                # For GitHub's format, the key is already in the right format
                # Let's try importing it directly
                $rsa.ImportRSAPublicKey($publicKeyBytes, [ref]$null)
            }
            
        } finally {
            if (Test-Path $tempKeyFile) {
                Remove-Item $tempKeyFile -Force
            }
        }
        
        # Convert plaintext to bytes
        $plainTextBytes = [System.Text.Encoding]::UTF8.GetBytes($PlainText)
        
        # Encrypt using OAEP padding (SHA-1)
        $encryptedBytes = $rsa.Encrypt($plainTextBytes, $true)
        
        # Convert to base64
        $encryptedBase64 = [Convert]::ToBase64String($encryptedBytes)
        
        return $encryptedBase64
    } catch {
        # Fallback: Try with RSACryptoServiceProvider
        $rsa = New-Object System.Security.Cryptography.RSACryptoServiceProvider
        $rsa.ImportRSAPublicKey($publicKeyBytes, [ref]$null)
        
        $plainTextBytes = [System.Text.Encoding]::UTF8.GetBytes($PlainText)
        $encryptedBytes = $rsa.Encrypt($plainTextBytes, $true)
        $encryptedBase64 = [Convert]::ToBase64String($encryptedBytes)
        
        return $encryptedBase64
    } finally {
        if ($rsa) {
            $rsa.Dispose()
        }
    }
}

try {
    $encryptedUsername = Encrypt-GitHubSecret -PlainText $dockerhubUsername -PublicKeyBase64 $publicKey
    Write-Host "✅ DOCKERHUB_USERNAME encrypted" -ForegroundColor Green
    
    $encryptedToken = Encrypt-GitHubSecret -PlainText $dockerhubToken -PublicKeyBase64 $publicKey
    Write-Host "✅ DOCKERHUB_TOKEN encrypted" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to encrypt secrets: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Add secrets to GitHub
Write-Host ""
Write-Host "📤 Adding secrets to GitHub..." -ForegroundColor Cyan

# Add DOCKERHUB_USERNAME
Write-Host "   Adding DOCKERHUB_USERNAME..." -ForegroundColor Gray
try {
    $body = @{
        encrypted_value = $encryptedUsername
        key_id = $keyId
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "$baseUrl/DOCKERHUB_USERNAME" -Headers $headers -Method Put -Body $body -ContentType "application/json" | Out-Null
    Write-Host "✅ DOCKERHUB_USERNAME added successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add DOCKERHUB_USERNAME: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Add DOCKERHUB_TOKEN
Write-Host "   Adding DOCKERHUB_TOKEN..." -ForegroundColor Gray
try {
    $body = @{
        encrypted_value = $encryptedToken
        key_id = $keyId
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "$baseUrl/DOCKERHUB_TOKEN" -Headers $headers -Method Put -Body $body -ContentType "application/json" | Out-Null
    Write-Host "✅ DOCKERHUB_TOKEN added successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to add DOCKERHUB_TOKEN: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ All secrets added successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "✨ Next steps:" -ForegroundColor Cyan
Write-Host "   1. Re-run the failed workflow:" -ForegroundColor White
Write-Host "      https://github.com/$owner/$repo/actions" -ForegroundColor Yellow
Write-Host ""
Write-Host "   2. Or push a new commit to trigger a fresh build" -ForegroundColor White
Write-Host ""

