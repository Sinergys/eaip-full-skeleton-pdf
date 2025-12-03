Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
    [string]$Tag,
    [int]$WorkflowRunNumber = 0
)

if (-not $Tag) {
    $Tag = "v0.3.0"
}

Write-Host "🔍 Checking workflow status..." -ForegroundColor Cyan
Write-Host ""

# Get GitHub token
$token = [System.Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")
if (-not $token) {
    Write-Host "❌ GitHub token not found!" -ForegroundColor Red
    exit 1
}

$owner = "Sinergys"
$repo = "eaip-full-skeleton-pdf"

$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}

# Get workflow runs
$runsUrl = "https://api.github.com/repos/$owner/$repo/actions/runs?per_page=10"
$runs = Invoke-RestMethod -Uri $runsUrl -Headers $headers

# Find release workflow runs
$releaseRuns = $runs.workflow_runs | Where-Object { $_.name -like "*Release*" -or $_.name -like "*release*" }

if ($releaseRuns.Count -eq 0) {
    Write-Host "❌ No release workflow runs found" -ForegroundColor Red
    exit 1
}

# Get latest or specific run
if ($WorkflowRunNumber -gt 0) {
    $targetRun = $releaseRuns | Where-Object { $_.run_number -eq $WorkflowRunNumber } | Select-Object -First 1
} else {
    $targetRun = $releaseRuns | Select-Object -First 1
}

if (-not $targetRun) {
    Write-Host "❌ Workflow run not found" -ForegroundColor Red
    exit 1
}

$status = $targetRun.status
$conclusion = $targetRun.conclusion
$runNumber = $targetRun.run_number
$htmlUrl = $targetRun.html_url

Write-Host "📊 Workflow Status:" -ForegroundColor Cyan
Write-Host "  Name: $($targetRun.name)" -ForegroundColor Yellow
Write-Host "  Run #$runNumber" -ForegroundColor Gray
Write-Host "  Status: $status" -ForegroundColor $(if ($status -eq 'completed') { 'Green' } elseif ($status -eq 'in_progress') { 'Yellow' } else { 'Cyan' })
Write-Host "  Conclusion: $conclusion" -ForegroundColor $(if ($conclusion -eq 'success') { 'Green' } elseif ($conclusion -eq 'failure') { 'Red' } else { 'Yellow' })
Write-Host "  Tag: $($targetRun.head_branch)" -ForegroundColor Gray
Write-Host "  URL: $htmlUrl" -ForegroundColor Cyan
Write-Host ""

# Get job details
$jobsUrl = "https://api.github.com/repos/$owner/$repo/actions/runs/$($targetRun.id)/jobs"
$jobs = Invoke-RestMethod -Uri $jobsUrl -Headers $headers

Write-Host "📋 Jobs:" -ForegroundColor Cyan
foreach ($job in $jobs.jobs) {
    $jobStatus = $job.status
    $jobConclusion = $job.conclusion
    $statusColor = if ($jobConclusion -eq 'success') { 'Green' } elseif ($jobConclusion -eq 'failure') { 'Red' } elseif ($jobStatus -eq 'in_progress') { 'Yellow' } else { 'Gray' }
    
    Write-Host "  $($job.name): $jobStatus - $jobConclusion" -ForegroundColor $statusColor
    
    # Show failed steps
    if ($jobConclusion -eq 'failure') {
        foreach ($step in $job.steps) {
            if ($step.conclusion -eq 'failure') {
                Write-Host "    ❌ Failed: $($step.name)" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""

# Summary
if ($status -eq 'completed') {
    if ($conclusion -eq 'success') {
        Write-Host "✅ Workflow completed successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "✨ Next steps:" -ForegroundColor Cyan
        Write-Host "  1. Check Docker Hub: https://hub.docker.com/u/ecosinergys" -ForegroundColor White
        Write-Host "  2. Verify images have tags: :$Tag and :latest" -ForegroundColor White
        Write-Host "  3. (Optional) Verify signature:" -ForegroundColor White
        Write-Host "     cosign verify docker.io/ecosinergys/eaip-full-skeleton-gateway-auth:$Tag" -ForegroundColor Gray
    } else {
        Write-Host "❌ Workflow completed with errors" -ForegroundColor Red
        Write-Host "   Check details: $htmlUrl" -ForegroundColor Yellow
    }
} elseif ($status -eq 'in_progress') {
    Write-Host "⏳ Workflow is still running..." -ForegroundColor Yellow
    Write-Host "   Check progress: $htmlUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Run this script again in a few minutes to check status" -ForegroundColor Gray
} else {
    Write-Host "ℹ️  Workflow status: $status" -ForegroundColor Cyan
}

Write-Host ""

