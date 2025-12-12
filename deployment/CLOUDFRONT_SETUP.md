# SaveVia CloudFront + S3 Frontend Deployment Guide

## Architecture Overview

```
User Request
    ↓
CloudFront (CDN)
    ↓
S3 Bucket (Static Files)

API Requests (api.savevia.app) → EC2 (Nginx → Gateway → Services)
```

## Step 1: Create S3 Bucket

### 1.1 Create Bucket
```bash
aws s3 mb s3://savevia-web-prod --region ca-central-1
```

### 1.2 Configure Bucket for Static Website
```bash
# Disable block public access (CloudFront will use OAI)
aws s3api put-public-access-block \
    --bucket savevia-web-prod \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=false,RestrictPublicBuckets=false"
```

### 1.3 Bucket Policy (Allow CloudFront OAI)
Create `bucket-policy.json`:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowCloudFrontOAI",
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity YOUR_OAI_ID"
            },
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::savevia-web-prod/*"
        }
    ]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy --bucket savevia-web-prod --policy file://bucket-policy.json
```

## Step 2: Request SSL Certificate (ACM)

### 2.1 Request Certificate
```bash
# Must be in us-east-1 for CloudFront!
aws acm request-certificate \
    --domain-name savevia.app \
    --subject-alternative-names "*.savevia.app" \
    --validation-method DNS \
    --region us-east-1
```

### 2.2 Validate Certificate
1. Go to AWS Console → Certificate Manager (us-east-1)
2. Click on the certificate
3. Click "Create records in Route 53" to auto-validate
4. Wait for status to become "Issued"

## Step 3: Create CloudFront Distribution

### 3.1 Create Origin Access Identity (OAI)
```bash
aws cloudfront create-cloud-front-origin-access-identity \
    --cloud-front-origin-access-identity-config \
    CallerReference=$(date +%s),Comment="SaveVia OAI"
```

Save the returned OAI ID.

### 3.2 Create Distribution
Create `cloudfront-config.json`:
```json
{
    "CallerReference": "savevia-web-2024",
    "Comment": "SaveVia Frontend",
    "Enabled": true,
    "Aliases": {
        "Quantity": 1,
        "Items": ["savevia.app"]
    },
    "DefaultRootObject": "index.html",
    "Origins": {
        "Quantity": 1,
        "Items": [
            {
                "Id": "S3-savevia-web-prod",
                "DomainName": "savevia-web-prod.s3.ca-central-1.amazonaws.com",
                "S3OriginConfig": {
                    "OriginAccessIdentity": "origin-access-identity/cloudfront/YOUR_OAI_ID"
                }
            }
        ]
    },
    "DefaultCacheBehavior": {
        "TargetOriginId": "S3-savevia-web-prod",
        "ViewerProtocolPolicy": "redirect-to-https",
        "AllowedMethods": {
            "Quantity": 2,
            "Items": ["GET", "HEAD"],
            "CachedMethods": {
                "Quantity": 2,
                "Items": ["GET", "HEAD"]
            }
        },
        "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
        "Compress": true
    },
    "CacheBehaviors": {
        "Quantity": 2,
        "Items": [
            {
                "PathPattern": "/index.html",
                "TargetOriginId": "S3-savevia-web-prod",
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                    "CachedMethods": {
                        "Quantity": 2,
                        "Items": ["GET", "HEAD"]
                    }
                },
                "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                "Compress": true
            },
            {
                "PathPattern": "/assets/*",
                "TargetOriginId": "S3-savevia-web-prod",
                "ViewerProtocolPolicy": "redirect-to-https",
                "AllowedMethods": {
                    "Quantity": 2,
                    "Items": ["GET", "HEAD"],
                    "CachedMethods": {
                        "Quantity": 2,
                        "Items": ["GET", "HEAD"]
                    }
                },
                "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
                "Compress": true
            }
        ]
    },
    "CustomErrorResponses": {
        "Quantity": 2,
        "Items": [
            {
                "ErrorCode": 403,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 10
            },
            {
                "ErrorCode": 404,
                "ResponsePagePath": "/index.html",
                "ResponseCode": "200",
                "ErrorCachingMinTTL": 10
            }
        ]
    },
    "ViewerCertificate": {
        "ACMCertificateArn": "YOUR_CERTIFICATE_ARN",
        "SSLSupportMethod": "sni-only",
        "MinimumProtocolVersion": "TLSv1.2_2021"
    },
    "PriceClass": "PriceClass_100",
    "HttpVersion": "http2and3"
}
```

Create distribution:
```bash
aws cloudfront create-distribution --distribution-config file://cloudfront-config.json
```

## Step 4: Configure Route 53 DNS

### 4.1 Create Hosted Zone (if not exists)
```bash
aws route53 create-hosted-zone --name savevia.app --caller-reference $(date +%s)
```

### 4.2 Add DNS Records
```bash
# A record for savevia.app → CloudFront
aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "savevia.app",
                "Type": "A",
                "AliasTarget": {
                    "HostedZoneId": "Z2FDTNDATAQYW2",
                    "DNSName": "YOUR_CLOUDFRONT_DOMAIN.cloudfront.net",
                    "EvaluateTargetHealth": false
                }
            }
        }]
    }'

# A record for api.savevia.app → EC2
aws route53 change-resource-record-sets \
    --hosted-zone-id YOUR_ZONE_ID \
    --change-batch '{
        "Changes": [{
            "Action": "CREATE",
            "ResourceRecordSet": {
                "Name": "api.savevia.app",
                "Type": "A",
                "TTL": 300,
                "ResourceRecords": [{"Value": "YOUR_EC2_IP"}]
            }
        }]
    }'
```

## Step 5: Deploy Frontend

### 5.1 Build Frontend
```bash
cd savevia-web
npm run build
```

### 5.2 Upload to S3
```bash
# Sync all files
aws s3 sync dist/ s3://savevia-web-prod/ --delete

# Set correct content types
aws s3 cp s3://savevia-web-prod/ s3://savevia-web-prod/ \
    --exclude "*" --include "*.js" \
    --content-type "application/javascript" \
    --metadata-directive REPLACE --recursive

aws s3 cp s3://savevia-web-prod/ s3://savevia-web-prod/ \
    --exclude "*" --include "*.css" \
    --content-type "text/css" \
    --metadata-directive REPLACE --recursive
```

### 5.3 Invalidate CloudFront Cache
```bash
aws cloudfront create-invalidation \
    --distribution-id YOUR_DISTRIBUTION_ID \
    --paths "/*"
```

## Step 6: Frontend Environment Variables

Create `.env.production` in savevia-web:
```bash
VITE_API_BASE_URL=https://api.savevia.app
VITE_GOOGLE_CLIENT_ID=your-google-client-id
VITE_APPLE_CLIENT_ID=com.savevia.app
VITE_REVENUECAT_IOS_API_KEY=your-revenuecat-key
```

## Deployment Script

Create `deploy-frontend.sh`:
```bash
#!/bin/bash
set -e

echo "Building frontend..."
cd savevia-web
npm run build

echo "Uploading to S3..."
aws s3 sync dist/ s3://savevia-web-prod/ --delete

echo "Invalidating CloudFront cache..."
aws cloudfront create-invalidation \
    --distribution-id YOUR_DISTRIBUTION_ID \
    --paths "/*"

echo "Frontend deployed successfully!"
```

## Cache Policies

| Path | Cache TTL | Notes |
|------|-----------|-------|
| `/index.html` | 0 (no cache) | Always fresh for SPA routing |
| `/assets/*` | 1 year | Hashed filenames, immutable |
| `/*.js`, `/*.css` | 1 year | Vite adds hashes |
| `/logos/*` | 1 day | Static images |

## Estimated Monthly Costs

| Service | Cost |
|---------|------|
| S3 Storage (1GB) | $0.02 |
| S3 Requests (1M) | $0.40 |
| CloudFront (100GB) | $8.50 |
| Route 53 Hosted Zone | $0.50 |
| **Total** | ~$10/month |

## Troubleshooting

### 403 Forbidden
- Check OAI is correct in bucket policy
- Verify CloudFront origin settings

### SPA Routing Issues (404)
- Ensure custom error responses redirect to index.html
- Check CloudFront cache behavior for index.html

### Stale Content
- Create CloudFront invalidation
- Check browser cache
- Verify S3 sync completed
