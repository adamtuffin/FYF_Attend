# Find Your Feet CIC - Deployment Guide

This guide covers deploying the Course Attendance Registration application to AWS.

## Prerequisites

1. **AWS CLI** - Configured with appropriate credentials
   ```bash
   aws configure
   ```

2. **AWS SAM CLI** - For serverless deployments
   ```bash
   # Windows (via Chocolatey)
   choco install aws-sam-cli
   
   # macOS (via Homebrew)
   brew install aws-sam-cli
   
   # Linux
   pip install aws-sam-cli
   ```

3. **Python 3.11+** - For Lambda runtime

4. **Node.js 18+** - For Tailwind CSS builds

5. **Docker** - Required for SAM build with `--use-container`

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      CloudFront CDN                         │
│  (HTTPS termination, caching, global distribution)          │
└─────────────────────────────────────────────────────────────┘
                    │                    │
                    ▼                    ▼
        ┌───────────────────┐  ┌───────────────────┐
        │   API Gateway     │  │    S3 Bucket      │
        │   (REST API)      │  │  (Static Assets)  │
        └───────────────────┘  └───────────────────┘
                    │
                    ▼
        ┌───────────────────┐
        │  Lambda Function  │
        │   (Flask App)     │
        └───────────────────┘
                    │
                    ▼
        ┌───────────────────┐
        │    DynamoDB       │
        │  (Attendance)     │
        └───────────────────┘
```

## Deployment Commands

### Quick Deploy (Development)

```powershell
# Windows PowerShell
.\deploy.ps1 -Environment development
```

```bash
# Linux/macOS
./deploy.sh development
```

### Manual Step-by-Step

1. **Build the application**:
   ```bash
   cd backend
   sam build --use-container
   ```

2. **Deploy to AWS**:
   ```bash
   # Development
   sam deploy --config-env development
   
   # Staging
   sam deploy --config-env staging
   
   # Production
   sam deploy --config-env production
   ```

3. **Upload static assets**:
   ```bash
   # Get bucket name from CloudFormation outputs
   BUCKET=$(aws cloudformation describe-stacks --stack-name fyf-attendance-dev \
     --query "Stacks[0].Outputs[?OutputKey=='StaticAssetsBucketName'].OutputValue" --output text)
   
   # Build CSS
   cd frontend
   npm run build
   
   # Sync to S3
   aws s3 sync static/ s3://$BUCKET/static/ --delete
   ```

4. **Invalidate CloudFront cache** (if needed):
   ```bash
   DIST_ID=$(aws cloudformation describe-stacks --stack-name fyf-attendance-dev \
     --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" --output text)
   
   aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
   ```

## Environment Configuration

### Stack Names by Environment

| Environment | Stack Name | SAM Config |
|-------------|------------|------------|
| Development | fyf-attendance-dev | `--config-env development` |
| Staging | fyf-attendance-staging | `--config-env staging` |
| Production | fyf-attendance-prod | `--config-env production` |

### Environment Variables

The following environment variables are set automatically in Lambda:

| Variable | Description |
|----------|-------------|
| `ENVIRONMENT` | Current environment (development/staging/production) |
| `LOCAL_MODE` | Always `false` in AWS |
| `DYNAMODB_TABLE_NAME` | DynamoDB table name |
| `LOG_LEVEL` | INFO for production, DEBUG otherwise |

## Outputs

After deployment, these outputs are available:

| Output | Description |
|--------|-------------|
| `CloudFrontUrl` | **Use this URL** - The main application URL |
| `ApiUrl` | Direct API Gateway URL (for debugging) |
| `StaticAssetsBucketName` | S3 bucket for static files |
| `CloudFrontDistributionId` | For cache invalidation |
| `TableName` | DynamoDB table name |

## Costs

This serverless architecture is cost-effective:

| Service | Pricing Model |
|---------|---------------|
| Lambda | Pay per request (1M free/month) |
| API Gateway | Pay per request ($3.50/million) |
| DynamoDB | Pay per request |
| S3 | Pay per GB stored |
| CloudFront | Pay per GB transferred |

Estimated cost for small charity: **< £5/month**

## Troubleshooting

### Build Fails
```bash
# Clear SAM build cache
rm -rf .aws-sam
sam build --use-container
```

### Lambda Timeout
- Check CloudWatch Logs: `/aws/lambda/fyf-attendance-{env}`
- Increase timeout in template.yaml (default: 30s)

### Static Assets Not Loading
1. Verify S3 sync completed
2. Check CloudFront cache invalidation
3. Verify bucket policy allows CloudFront access

### CORS Errors
- CORS is configured in API Gateway
- Check browser console for specific errors

## Rollback

To rollback to a previous version:

```bash
# List stack events to find previous version
aws cloudformation describe-stack-events --stack-name fyf-attendance-dev

# Rollback (CloudFormation will use last successful state)
aws cloudformation rollback-stack --stack-name fyf-attendance-dev
```

## Deleting the Stack

⚠️ **Warning**: This will delete all resources including data!

```bash
# First, empty the S3 bucket
aws s3 rm s3://fyf-attendance-static-development-{account-id}/ --recursive

# Then delete the stack
sam delete --config-env development
```

Note: DynamoDB table has `DeletionPolicy: Retain` so data is preserved even if stack is deleted.
