#!/bin/bash

# =====================================================
# SaveVia Frontend Deployment Script
# Deploy React app to S3 + CloudFront
# Domain: savevia.app
# =====================================================

set -e

# Configuration - Update these values
S3_BUCKET="${S3_BUCKET:-savevia-web-prod}"
CLOUDFRONT_DISTRIBUTION_ID="${CLOUDFRONT_DISTRIBUTION_ID:-}"
AWS_REGION="${AWS_REGION:-ca-central-1}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_msg() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_msg "Checking prerequisites..."

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed"
        exit 1
    fi

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure'"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Build frontend
build_frontend() {
    print_msg "Building frontend..."
    cd "$PROJECT_ROOT/savevia-web"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_msg "Installing dependencies..."
        npm install
    fi

    # Build
    npm run build

    if [ -d "dist" ]; then
        print_success "Frontend build completed"
    else
        print_error "Build failed - dist directory not found"
        exit 1
    fi
}

# Upload to S3
upload_to_s3() {
    print_msg "Uploading to S3 bucket: $S3_BUCKET..."
    cd "$PROJECT_ROOT/savevia-web"

    # Sync all files
    aws s3 sync dist/ "s3://${S3_BUCKET}/" \
        --delete \
        --region "$AWS_REGION"

    # Set cache headers for index.html (no cache)
    aws s3 cp "s3://${S3_BUCKET}/index.html" "s3://${S3_BUCKET}/index.html" \
        --metadata-directive REPLACE \
        --cache-control "no-cache, no-store, must-revalidate" \
        --content-type "text/html" \
        --region "$AWS_REGION"

    # Set cache headers for JS files (1 year) with correct content-type
    aws s3 cp "s3://${S3_BUCKET}/assets/" "s3://${S3_BUCKET}/assets/" \
        --recursive \
        --exclude "*" \
        --include "*.js" \
        --metadata-directive REPLACE \
        --content-type "application/javascript" \
        --cache-control "public, max-age=31536000, immutable" \
        --region "$AWS_REGION"

    # Set cache headers for CSS files (1 year) with correct content-type
    aws s3 cp "s3://${S3_BUCKET}/assets/" "s3://${S3_BUCKET}/assets/" \
        --recursive \
        --exclude "*" \
        --include "*.css" \
        --metadata-directive REPLACE \
        --content-type "text/css" \
        --cache-control "public, max-age=31536000, immutable" \
        --region "$AWS_REGION"

    print_success "Files uploaded to S3"
}

# Invalidate CloudFront cache
invalidate_cloudfront() {
    if [ -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
        print_warning "CLOUDFRONT_DISTRIBUTION_ID not set, skipping invalidation"
        return
    fi

    print_msg "Invalidating CloudFront cache..."

    aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --paths "/*" \
        --region us-east-1

    print_success "CloudFront cache invalidation initiated"
}

# Print deployment info
print_deployment_info() {
    echo ""
    echo "========================================"
    echo "Deployment Summary"
    echo "========================================"
    echo "S3 Bucket:      $S3_BUCKET"
    echo "CloudFront ID:  ${CLOUDFRONT_DISTRIBUTION_ID:-Not configured}"
    echo "Region:         $AWS_REGION"
    echo ""
    echo "URLs:"
    echo "  S3:           http://${S3_BUCKET}.s3-website.${AWS_REGION}.amazonaws.com"
    echo "  Production:   https://savevia.app"
    echo "========================================"
}

# Main
main() {
    case "${1:-deploy}" in
        deploy)
            check_prerequisites
            build_frontend
            upload_to_s3
            invalidate_cloudfront
            print_deployment_info
            print_success "Frontend deployment completed!"
            ;;
        build)
            build_frontend
            print_success "Build completed!"
            ;;
        upload)
            check_prerequisites
            upload_to_s3
            print_success "Upload completed!"
            ;;
        invalidate)
            check_prerequisites
            invalidate_cloudfront
            print_success "Cache invalidation completed!"
            ;;
        help|--help|-h)
            echo "SaveVia Frontend Deployment Script"
            echo ""
            echo "Usage: ./deploy-frontend.sh [command]"
            echo ""
            echo "Commands:"
            echo "  deploy      Full deployment (build, upload, invalidate)"
            echo "  build       Build only"
            echo "  upload      Upload to S3 only"
            echo "  invalidate  Invalidate CloudFront cache only"
            echo ""
            echo "Environment Variables:"
            echo "  S3_BUCKET                    S3 bucket name (default: savevia-web-prod)"
            echo "  CLOUDFRONT_DISTRIBUTION_ID   CloudFront distribution ID"
            echo "  AWS_REGION                   AWS region (default: ca-central-1)"
            ;;
        *)
            print_error "Unknown command: $1"
            exit 1
            ;;
    esac
}

main "$@"
