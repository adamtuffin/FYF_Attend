#!/bin/bash
# Find Your Feet CIC - Course Attendance Registration
# Deployment Script for AWS (Bash version)
#
# Prerequisites:
#   - AWS CLI configured with appropriate credentials
#   - AWS SAM CLI installed
#   - Python 3.11+
#
# Usage:
#   ./deploy.sh development
#   ./deploy.sh staging
#   ./deploy.sh production

set -e

ENVIRONMENT=${1:-development}
SKIP_BUILD=${SKIP_BUILD:-false}
SKIP_STATIC=${SKIP_STATIC:-false}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "Error: Invalid environment. Use: development, staging, or production"
    exit 1
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "Find Your Feet - Deployment Script"
echo "Environment: $ENVIRONMENT"
echo "========================================"

# Navigate to backend directory
cd "$PROJECT_ROOT/backend"

# Step 1: Build the SAM application
if [ "$SKIP_BUILD" != "true" ]; then
    echo -e "\n[1/4] Building SAM application..."
    sam build --use-container
else
    echo -e "\n[1/4] Skipping SAM build..."
fi

# Step 2: Deploy the SAM application
echo -e "\n[2/4] Deploying to AWS ($ENVIRONMENT)..."
sam deploy --config-env "$ENVIRONMENT"

# Step 3: Get the S3 bucket name from CloudFormation outputs
echo -e "\n[3/4] Getting stack outputs..."

case $ENVIRONMENT in
    development) STACK_NAME="fyf-attendance-dev" ;;
    staging) STACK_NAME="fyf-attendance-staging" ;;
    production) STACK_NAME="fyf-attendance-prod" ;;
esac

S3_BUCKET=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='StaticAssetsBucketName'].OutputValue" --output text)
CLOUDFRONT_ID=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" --output text)
CLOUDFRONT_URL=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue" --output text)
API_URL=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text)

echo "  S3 Bucket: $S3_BUCKET"
echo "  CloudFront ID: $CLOUDFRONT_ID"

# Step 4: Upload static assets to S3
if [ "$SKIP_STATIC" != "true" ]; then
    echo -e "\n[4/4] Uploading static assets to S3..."
    
    # Build Tailwind CSS first
    cd "$PROJECT_ROOT/frontend"
    echo "  Building CSS..."
    npm run build
    
    # Sync static files to S3
    echo "  Syncing to S3..."
    aws s3 sync static/ "s3://$S3_BUCKET/static/" --delete --cache-control "max-age=31536000,public"
    
    # Invalidate CloudFront cache
    echo "  Invalidating CloudFront cache..."
    aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_ID" --paths "/static/*" > /dev/null
else
    echo -e "\n[4/4] Skipping static assets upload..."
fi

# Done!
echo -e "\n========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Application URL: $CLOUDFRONT_URL"
echo "API Gateway URL: $API_URL"
echo ""
echo "Note: CloudFront may take a few minutes to propagate changes."
