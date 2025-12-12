# SaveVia AWS Deployment Guide

## Architecture Overview

```
                    ┌─────────────────────────────────────────────────────┐
                    │                    Route 53                          │
                    │    savevia.app → CloudFront                          │
                    │    api.savevia.app → EC2                             │
                    └─────────────────────────────────────────────────────┘
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    │                                           │
                    ▼                                           ▼
        ┌───────────────────┐                       ┌───────────────────┐
        │    CloudFront     │                       │       EC2         │
        │   (Frontend CDN)  │                       │   (t3.medium)     │
        │                   │                       │                   │
        │  ┌─────────────┐  │                       │  ┌─────────────┐  │
        │  │  S3 Bucket  │  │                       │  │   Nginx     │  │
        │  │ (React App) │  │                       │  │   (SSL)     │  │
        │  └─────────────┘  │                       │  └──────┬──────┘  │
        └───────────────────┘                       │         │         │
                                                    │         ▼         │
                                                    │  ┌─────────────┐  │
                                                    │  │   Docker    │  │
                                                    │  │  Compose    │  │
                                                    │  └──────┬──────┘  │
                                                    │         │         │
                                                    └─────────┼─────────┘
                                                              │
              ┌───────────────┬───────────────┬───────────────┼───────────────┬───────────────┐
              │               │               │               │               │               │
              ▼               ▼               ▼               ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  Eureka  │   │ Gateway  │   │   User   │   │   Card   │   │Optimizer │   │ RabbitMQ │
        │  :8761   │   │  :8080   │   │  :8081   │   │  :8082   │   │  :8083   │   │  :5672   │
        └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
                                            │               │               │
                                            └───────────────┼───────────────┘
                                                            │
                                            ┌───────────────┼───────────────┐
                                            │               │               │
                                            ▼               ▼               ▼
                                      ┌──────────┐   ┌──────────┐   ┌──────────┐
                                      │   RDS    │   │ElastiCache│   │    S3    │
                                      │  MySQL   │   │   Redis   │   │ Uploads  │
                                      └──────────┘   └──────────┘   └──────────┘
```

## Prerequisites

### Local Machine
- Docker Desktop
- Maven 3.8+
- JDK 17
- Node.js 18+
- AWS CLI v2

### AWS Account
- IAM user with admin access
- Region: ca-central-1 (Canada)

## Step 1: AWS Infrastructure Setup

### 1.1 Create VPC and Networking
```bash
# Create VPC
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=savevia-vpc}]'

# Create subnets, internet gateway, route tables...
# (Or use AWS Console for easier setup)
```

### 1.2 Create RDS MySQL Instance
```bash
aws rds create-db-instance \
    --db-instance-identifier savevia-prod-db \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --engine-version 8.0 \
    --master-username savevia_admin \
    --master-user-password YOUR_PASSWORD \
    --allocated-storage 20 \
    --region ca-central-1
```

After RDS is ready, connect and run initialization scripts:
```bash
mysql -h savevia-prod-db.xxx.ca-central-1.rds.amazonaws.com -u savevia_admin -p < docker/mysql/init/01-schema.sql
mysql -h savevia-prod-db.xxx.ca-central-1.rds.amazonaws.com -u savevia_admin -p < docker/mysql/init/02-seed-cards.sql
# ... run all init scripts
```

### 1.3 Create ElastiCache Redis
```bash
aws elasticache create-cache-cluster \
    --cache-cluster-id savevia-prod-redis \
    --engine redis \
    --cache-node-type cache.t3.micro \
    --num-cache-nodes 1 \
    --region ca-central-1
```

### 1.4 Create EC2 Instance
```bash
# Launch t3.medium with Ubuntu 22.04
aws ec2 run-instances \
    --image-id ami-0c9bfc21ac5bf10eb \
    --instance-type t3.medium \
    --key-name savevia-prod \
    --security-group-ids sg-xxx \
    --subnet-id subnet-xxx \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=savevia-prod}]'
```

### 1.5 Configure EC2 Instance
SSH into EC2 and run:
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx
```

## Step 2: Configure Environment

### 2.1 Create Production .env
```bash
cp deployment/.env.template deployment/.env
# Edit deployment/.env with your production values
```

## Step 3: Deploy Backend

### 3.1 Full Deployment
```bash
export EC2_HOST=your-ec2-ip
export EC2_KEY=~/.ssh/savevia-prod.pem

./deployment/deploy.sh full
```

### 3.2 Individual Commands
```bash
# Build only
./deployment/deploy.sh build

# Upload only
./deployment/deploy.sh upload

# Deploy on EC2 only
./deployment/deploy.sh deploy

# Verify health
./deployment/deploy.sh verify

# View logs
./deployment/deploy.sh logs gateway
```

### 3.3 Setup Nginx & SSL
```bash
./deployment/deploy.sh nginx
./deployment/deploy.sh ssl
```

## Step 4: Deploy Frontend

### 4.1 Create S3 Bucket
```bash
aws s3 mb s3://savevia-web-prod --region ca-central-1
```

### 4.2 Setup CloudFront
Follow the detailed guide: [CLOUDFRONT_SETUP.md](./CLOUDFRONT_SETUP.md)

### 4.3 Deploy Frontend
```bash
export S3_BUCKET=savevia-web-prod
export CLOUDFRONT_DISTRIBUTION_ID=EXXXXX

./deployment/deploy-frontend.sh deploy
```

## Step 5: DNS Configuration

### Route 53 Records
| Record | Type | Value |
|--------|------|-------|
| savevia.app | A | CloudFront alias |
| api.savevia.app | A | EC2 IP |

## Directory Structure

```
deployment/
├── README.md                    # This file
├── CLOUDFRONT_SETUP.md          # CloudFront setup guide
├── deploy.sh                    # Backend deployment script
├── deploy-frontend.sh           # Frontend deployment script
├── docker-compose.production.yml # Production compose file
├── .env.template                # Environment template
├── docker/
│   ├── Dockerfile.eureka
│   ├── Dockerfile.gateway
│   ├── Dockerfile.user
│   ├── Dockerfile.card
│   └── Dockerfile.optimizer
└── nginx/
    └── savevia.conf             # Nginx configuration
```

## Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Eureka | 8761 | Service Discovery |
| Gateway | 8080 | API Gateway |
| User Service | 8081 | Authentication, Users |
| Card Service | 8082 | Credit Card Data |
| Optimizer Service | 8083 | Cashback Engine, AI |
| RabbitMQ | 5672/15672 | Message Queue |

## Health Check Endpoints

```bash
# Eureka
curl http://api.savevia.app:8761/actuator/health

# Gateway
curl https://api.savevia.app/actuator/health

# Services (internal)
curl http://localhost:8081/actuator/health
curl http://localhost:8082/actuator/health
curl http://localhost:8083/actuator/health
```

## Monitoring & Logs

### View Docker Logs
```bash
ssh -i ~/.ssh/savevia-prod.pem ubuntu@EC2_IP
cd ~/savevia
docker-compose logs -f gateway
docker-compose logs -f user-service
```

### CloudWatch (Optional)
Configure CloudWatch agent for centralized logging.

## Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs eureka-server
docker-compose logs gateway

# Check if RDS/Redis are accessible
nc -zv RDS_HOST 3306
nc -zv REDIS_HOST 6379
```

### 502 Bad Gateway
```bash
# Check if gateway is running
docker ps
curl localhost:8080/actuator/health

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Database connection issues
```bash
# Test RDS connection from EC2
mysql -h RDS_HOST -u savevia_admin -p

# Check security groups allow EC2 → RDS
```

## Estimated Monthly Costs

| Service | Spec | Cost |
|---------|------|------|
| EC2 | t3.medium | $35 |
| RDS MySQL | db.t3.micro | $30 |
| ElastiCache | cache.t3.micro | $25 |
| S3 + CloudFront | 100GB | $10 |
| Data Transfer | ~$5 |
| **Total** | | **~$105/month** |

## Security Checklist

- [ ] RDS not publicly accessible
- [ ] Security groups properly configured
- [ ] SSL certificates installed
- [ ] Secrets in .env, not in code
- [ ] IAM roles for EC2 (no hardcoded keys)
- [ ] Regular backups enabled for RDS
- [ ] CloudWatch alarms configured
