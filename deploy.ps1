<# 
Find Your Feet CIC - Course Attendance Registration
Deployment Script for AWS

Prerequisites:
  - AWS CLI configured with appropriate credentials
  - AWS SAM CLI installed
  - Python 3.11+

Usage:
  .\deploy.ps1 -Environment development
  .\deploy.ps1 -Environment staging
  .\deploy.ps1 -Environment production
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('development', 'staging', 'production')]
    [string]$Environment,
    
    [switch]$SkipBuild,
    [switch]$SkipStaticAssets
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $ProjectRoot) { $ProjectRoot = Get-Location }

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Find Your Feet - Deployment Script" -ForegroundColor Cyan
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Navigate to backend directory
Set-Location "$ProjectRoot\backend"

# Step 1: Build the SAM application
if (-not $SkipBuild) {
    Write-Host "`n[1/4] Building SAM application..." -ForegroundColor Green
    sam build --use-container
    if ($LASTEXITCODE -ne 0) {
        Write-Host "SAM build failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[1/4] Skipping SAM build..." -ForegroundColor Yellow
}

# Step 2: Deploy the SAM application
Write-Host "`n[2/4] Deploying to AWS ($Environment)..." -ForegroundColor Green
sam deploy --config-env $Environment
if ($LASTEXITCODE -ne 0) {
    Write-Host "SAM deployment failed!" -ForegroundColor Red
    exit 1
}

# Step 3: Get the S3 bucket name from CloudFormation outputs
Write-Host "`n[3/4] Getting stack outputs..." -ForegroundColor Green
$StackName = "fyf-attendance-$Environment"
if ($Environment -eq "development") { $StackName = "fyf-attendance-dev" }
if ($Environment -eq "production") { $StackName = "fyf-attendance-prod" }

$Outputs = aws cloudformation describe-stacks --stack-name $StackName --query "Stacks[0].Outputs" | ConvertFrom-Json

$S3Bucket = ($Outputs | Where-Object { $_.OutputKey -eq "StaticAssetsBucketName" }).OutputValue
$CloudFrontId = ($Outputs | Where-Object { $_.OutputKey -eq "CloudFrontDistributionId" }).OutputValue
$CloudFrontUrl = ($Outputs | Where-Object { $_.OutputKey -eq "CloudFrontUrl" }).OutputValue
$ApiUrl = ($Outputs | Where-Object { $_.OutputKey -eq "ApiUrl" }).OutputValue

Write-Host "  S3 Bucket: $S3Bucket" -ForegroundColor Gray
Write-Host "  CloudFront ID: $CloudFrontId" -ForegroundColor Gray

# Step 4: Upload static assets to S3
if (-not $SkipStaticAssets) {
    Write-Host "`n[4/4] Uploading static assets to S3..." -ForegroundColor Green
    
    # Build Tailwind CSS first
    Set-Location "$ProjectRoot\frontend"
    Write-Host "  Building CSS..." -ForegroundColor Gray
    npm run build
    
    # Sync static files to S3
    Write-Host "  Syncing to S3..." -ForegroundColor Gray
    aws s3 sync static/ "s3://$S3Bucket/static/" --delete --cache-control "max-age=31536000,public"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "S3 sync failed!" -ForegroundColor Red
        exit 1
    }
    
    # Invalidate CloudFront cache
    Write-Host "  Invalidating CloudFront cache..." -ForegroundColor Gray
    aws cloudfront create-invalidation --distribution-id $CloudFrontId --paths "/static/*" | Out-Null
} else {
    Write-Host "`n[4/4] Skipping static assets upload..." -ForegroundColor Yellow
}

# Done!
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nApplication URL: $CloudFrontUrl" -ForegroundColor Yellow
Write-Host "API Gateway URL: $ApiUrl" -ForegroundColor Gray
Write-Host "`nNote: CloudFront may take a few minutes to propagate changes." -ForegroundColor Gray
