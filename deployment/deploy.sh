#!/bin/bash

# =====================================================
# SaveVia Deployment Script
# Deploy backend services to AWS EC2
# Domain: savevia.app
# =====================================================

set -e

# Configuration
EC2_HOST="${EC2_HOST:-3.96.214.173}"
EC2_USER="${EC2_USER:-ubuntu}"
EC2_KEY="${EC2_KEY:-$HOME/.ssh/savevia-prod.pem}"
DEPLOY_DIR="/home/${EC2_USER}/savevia"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# All available services
ALL_SERVICES=("eureka-server" "gateway" "user-service" "card-service" "optimizer-service" "savevia-ai")

# Get module name for service (used to locate the Maven module)
get_module() {
    case "$1" in
        "eureka-server") echo "savevia-eureka" ;;
        "gateway") echo "savevia-gateway" ;;
        "user-service") echo "savevia-user" ;;
        "card-service") echo "savevia-card" ;;
        "optimizer-service") echo "savevia-optimizer" ;;
        "savevia-ai") echo "savevia-ai" ;;
        *) echo "" ;;
    esac
}

# Get Dockerfile name for service (Java services live in deployment/docker/;
# Python service has its own Dockerfile inside the module root).
get_dockerfile() {
    case "$1" in
        "eureka-server") echo "Dockerfile.eureka" ;;
        "gateway") echo "Dockerfile.gateway" ;;
        "user-service") echo "Dockerfile.user" ;;
        "card-service") echo "Dockerfile.card" ;;
        "optimizer-service") echo "Dockerfile.optimizer" ;;
        "savevia-ai") echo "savevia-ai/Dockerfile" ;;
        *) echo "" ;;
    esac
}

# Return 0 (success) if the service is the Python service (skip Maven).
is_python_service() {
    [ "$1" = "savevia-ai" ]
}

# Print colored message
print_msg() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_step() {
    echo -e "${CYAN}>>> $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_msg "Checking prerequisites..."

    if [ ! -f "$EC2_KEY" ]; then
        print_error "SSH key not found: $EC2_KEY"
        exit 1
    fi

    # Check if maven is installed
    if ! command -v mvn &> /dev/null; then
        print_error "Maven is not installed"
        exit 1
    fi

    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Interactive service selector
select_services() {
    echo ""
    echo -e "${CYAN}Select services to deploy:${NC}"
    echo "  0) All services"
    echo "  1) eureka-server"
    echo "  2) gateway"
    echo "  3) user-service"
    echo "  4) card-service"
    echo "  5) optimizer-service"
    echo "  6) savevia-ai"
    echo ""
    read -p "Enter numbers separated by space (e.g., '3 4 6'): " selection

    if [ "$selection" == "0" ] || [ -z "$selection" ]; then
        SELECTED_SERVICES=("${ALL_SERVICES[@]}")
    else
        SELECTED_SERVICES=()
        for num in $selection; do
            case $num in
                1) SELECTED_SERVICES+=("eureka-server") ;;
                2) SELECTED_SERVICES+=("gateway") ;;
                3) SELECTED_SERVICES+=("user-service") ;;
                4) SELECTED_SERVICES+=("card-service") ;;
                5) SELECTED_SERVICES+=("optimizer-service") ;;
                6) SELECTED_SERVICES+=("savevia-ai") ;;
            esac
        done
    fi

    echo ""
    print_msg "Selected services: ${SELECTED_SERVICES[*]}"
}

# Build specific services with Maven
build_services() {
    local services=("$@")
    print_msg "Building Java services: ${services[*]}"
    cd "$PROJECT_ROOT"

    for service in "${services[@]}"; do
        if is_python_service "$service"; then
            print_step "Skipping Maven build for $service (Python service)"
            continue
        fi
        local module=$(get_module "$service")
        if [ -n "$module" ]; then
            print_step "Building $module..."
            cd "$PROJECT_ROOT/$module"
            mvn clean package -DskipTests -q
            if [ $? -eq 0 ]; then
                print_success "$module built successfully"
            else
                print_error "Failed to build $module"
                exit 1
            fi
        fi
    done

    print_success "Maven build completed"
}

# Build Docker images for specific services
build_docker_images() {
    local services=("$@")
    print_msg "Building Docker images: ${services[*]}"
    cd "$PROJECT_ROOT"

    for service in "${services[@]}"; do
        local dockerfile=$(get_dockerfile "$service")
        if [ -z "$dockerfile" ]; then
            continue
        fi
        print_step "Building Docker image: savevia/${service}..."
        if is_python_service "$service"; then
            # Python service has its own Dockerfile + build context (savevia-ai/)
            docker build -t savevia/${service}:latest -f "${dockerfile}" "${PROJECT_ROOT}/savevia-ai"
        else
            docker build -t savevia/${service}:latest -f deployment/docker/${dockerfile} .
        fi
        if [ $? -eq 0 ]; then
            print_success "Docker image savevia/${service} built"
        else
            print_error "Failed to build Docker image: savevia/${service}"
            exit 1
        fi
    done

    print_success "Docker images built"
}

# Save Docker images to tar files
save_docker_images() {
    local services=("$@")
    print_msg "Saving Docker images: ${services[*]}"
    cd "$PROJECT_ROOT/deployment"

    mkdir -p images

    for service in "${services[@]}"; do
        print_step "Saving savevia/${service}..."
        docker save savevia/${service}:latest | gzip > images/${service}.tar.gz
        local size=$(ls -lh images/${service}.tar.gz | awk '{print $5}')
        print_success "Saved ${service}.tar.gz ($size)"
    done

    print_success "Docker images saved"
}

# Upload specific services to EC2
upload_to_ec2() {
    local services=("$@")
    print_msg "Uploading files to EC2..."

    # Create deployment directory on EC2
    ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" "mkdir -p ${DEPLOY_DIR}/images ${DEPLOY_DIR}/logs ${DEPLOY_DIR}/keys"

    # Upload docker-compose and .env
    print_step "Uploading docker-compose.yml..."
    scp -i "$EC2_KEY" "$PROJECT_ROOT/deployment/docker-compose.production.yml" \
        "${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/docker-compose.yml"

    if [ -f "$PROJECT_ROOT/deployment/.env" ]; then
        print_step "Uploading .env..."
        scp -i "$EC2_KEY" "$PROJECT_ROOT/deployment/.env" \
            "${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/.env"
    fi

    # Upload APNs key files if they exist
    if ls "$PROJECT_ROOT/scripts/"*.p8 1> /dev/null 2>&1; then
        print_step "Uploading APNs key files..."
        scp -i "$EC2_KEY" "$PROJECT_ROOT/scripts/"*.p8 \
            "${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/keys/"
        ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" "chmod 644 ${DEPLOY_DIR}/keys/*.p8"
        print_success "APNs key files uploaded"
    fi

    # Upload Docker images
    for service in "${services[@]}"; do
        local file="$PROJECT_ROOT/deployment/images/${service}.tar.gz"
        if [ -f "$file" ]; then
            local size=$(ls -lh "$file" | awk '{print $5}')
            print_step "Uploading ${service}.tar.gz ($size)..."
            scp -i "$EC2_KEY" "$file" "${EC2_USER}@${EC2_HOST}:${DEPLOY_DIR}/images/"
        else
            print_warning "Image file not found: ${service}.tar.gz"
        fi
    done

    print_success "Files uploaded to EC2"
}

# Load Docker images on EC2
load_docker_images() {
    local services=("$@")
    print_msg "Loading Docker images on EC2: ${services[*]}"

    for service in "${services[@]}"; do
        print_step "Loading ${service}..."
        ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" \
            "cd ~/savevia/images && gunzip -c ${service}.tar.gz | docker load"
    done

    print_success "Docker images loaded on EC2"
}

# Start/restart specific services on EC2
start_services() {
    local services=("$@")
    print_msg "Starting services on EC2: ${services[*]}"

    # Convert service names for docker-compose
    local compose_services=""
    for service in "${services[@]}"; do
        case $service in
            "eureka-server") compose_services+="eureka-server " ;;
            "gateway") compose_services+="gateway " ;;
            "user-service") compose_services+="user-service " ;;
            "card-service") compose_services+="card-service " ;;
            "optimizer-service") compose_services+="optimizer-service " ;;
            "savevia-ai") compose_services+="savevia-ai " ;;
        esac
    done

    ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" << EOF
        cd ~/savevia

        # Stop specific services
        for svc in ${compose_services}; do
            echo "Stopping \$svc..."
            docker-compose stop \$svc 2>/dev/null || true
            docker-compose rm -f \$svc 2>/dev/null || true
        done

        # Start specific services
        docker-compose up -d ${compose_services}

        echo "Services started"
EOF

    print_success "Services started on EC2"
}

# Start all services on EC2
start_all_services() {
    print_msg "Starting all services on EC2..."

    ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" << 'EOF'
        cd ~/savevia
        docker-compose down --remove-orphans || true
        docker-compose up -d
        echo "All services started"
EOF

    print_success "All services started on EC2"
}

# Verify deployment
verify_deployment() {
    print_msg "Verifying deployment (waiting 30s for services to start)..."
    sleep 30

    ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" << 'EOF'
        echo ""
        echo "Service Health Status:"
        echo "======================"

        check_health() {
            local name=$1
            local port=$2
            local path=${3:-/actuator/health}
            local status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${port}${path}" 2>/dev/null || echo "000")
            if [ "$status" == "200" ]; then
                echo "✓ $name (port $port): healthy"
            else
                echo "✗ $name (port $port): unhealthy (HTTP $status)"
            fi
        }

        check_health "Eureka Server" 8761
        check_health "Gateway" 8080
        check_health "User Service" 8081
        check_health "Card Service" 8082
        check_health "Optimizer Service" 8083
        # savevia-ai (FastAPI): healthcheck path is /ready, not /actuator/health
        check_health "SaveVia AI" 8002 /ready

        echo ""
        echo "Docker Container Status:"
        echo "========================"
        docker-compose ps
EOF

    print_success "Deployment verification completed"
}

# Show logs
show_logs() {
    local service=$1
    print_msg "Showing logs for ${service}..."

    ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" "cd ~/savevia && docker-compose logs -f --tail=100 ${service}"
}

# Show status
show_status() {
    print_msg "Checking service status..."

    ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" << 'EOF'
        cd ~/savevia
        echo ""
        echo "Docker Containers:"
        echo "=================="
        docker-compose ps

        echo ""
        echo "Resource Usage:"
        echo "==============="
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
EOF
}

# Clean up
cleanup() {
    print_msg "Cleaning up local images..."
    rm -rf "$PROJECT_ROOT/deployment/images"/*.tar.gz 2>/dev/null || true
    print_success "Local cleanup completed"
}

cleanup_remote() {
    print_msg "Cleaning up remote server..."
    ssh -i "$EC2_KEY" "${EC2_USER}@${EC2_HOST}" << 'EOF'
        docker system prune -f
        rm -rf ~/savevia/images/*.tar.gz
        echo "Remote cleanup completed"
EOF
    print_success "Remote cleanup completed"
}

# Print usage
usage() {
    echo ""
    echo -e "${CYAN}SaveVia Backend Deployment Script${NC}"
    echo ""
    echo "Usage: ./deploy.sh [command] [services...]"
    echo ""
    echo "Commands:"
    echo "  deploy              Interactive deploy (select services)"
    echo "  deploy-all          Deploy all services"
    echo "  deploy [services]   Deploy specific services"
    echo "                      e.g., ./deploy.sh deploy user-service card-service"
    echo ""
    echo "  build [services]    Build only (Maven + Docker)"
    echo "  upload [services]   Upload images to EC2"
    echo "  start [services]    Start services on EC2"
    echo "  restart [services]  Restart services on EC2"
    echo ""
    echo "  status              Show service status"
    echo "  verify              Verify deployment health"
    echo "  logs [service]      Show logs (default: gateway)"
    echo ""
    echo "  cleanup             Clean up local temp files"
    echo "  cleanup-remote      Clean up remote server"
    echo ""
    echo "Services:"
    echo "  eureka-server, gateway, user-service, card-service, optimizer-service, savevia-ai"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh deploy                    # Interactive selection"
    echo "  ./deploy.sh deploy-all                # Deploy all services"
    echo "  ./deploy.sh deploy user-service       # Deploy user-service only"
    echo "  ./deploy.sh deploy user-service card-service optimizer-service"
    echo "  ./deploy.sh logs user-service         # View user-service logs"
    echo "  ./deploy.sh status                    # Check status"
    echo ""
}

# Main
main() {
    local cmd="${1:-help}"
    shift || true

    case "$cmd" in
        deploy)
            check_prerequisites
            if [ $# -eq 0 ]; then
                select_services
            else
                SELECTED_SERVICES=("$@")
            fi
            build_services "${SELECTED_SERVICES[@]}"
            build_docker_images "${SELECTED_SERVICES[@]}"
            save_docker_images "${SELECTED_SERVICES[@]}"
            upload_to_ec2 "${SELECTED_SERVICES[@]}"
            load_docker_images "${SELECTED_SERVICES[@]}"
            start_services "${SELECTED_SERVICES[@]}"
            cleanup
            verify_deployment
            print_success "Deployment completed!"
            ;;
        deploy-all)
            check_prerequisites
            SELECTED_SERVICES=("${ALL_SERVICES[@]}")
            build_services "${SELECTED_SERVICES[@]}"
            build_docker_images "${SELECTED_SERVICES[@]}"
            save_docker_images "${SELECTED_SERVICES[@]}"
            upload_to_ec2 "${SELECTED_SERVICES[@]}"
            load_docker_images "${SELECTED_SERVICES[@]}"
            start_all_services
            cleanup
            verify_deployment
            print_success "Full deployment completed!"
            ;;
        build)
            check_prerequisites
            if [ $# -eq 0 ]; then
                select_services
            else
                SELECTED_SERVICES=("$@")
            fi
            build_services "${SELECTED_SERVICES[@]}"
            build_docker_images "${SELECTED_SERVICES[@]}"
            save_docker_images "${SELECTED_SERVICES[@]}"
            print_success "Build completed!"
            ;;
        upload)
            check_prerequisites
            if [ $# -eq 0 ]; then
                SELECTED_SERVICES=("${ALL_SERVICES[@]}")
            else
                SELECTED_SERVICES=("$@")
            fi
            upload_to_ec2 "${SELECTED_SERVICES[@]}"
            load_docker_images "${SELECTED_SERVICES[@]}"
            print_success "Upload completed!"
            ;;
        start|restart)
            check_prerequisites
            if [ $# -eq 0 ]; then
                start_all_services
            else
                start_services "$@"
            fi
            print_success "Services started!"
            ;;
        status)
            check_prerequisites
            show_status
            ;;
        verify)
            check_prerequisites
            verify_deployment
            ;;
        logs)
            check_prerequisites
            show_logs "${1:-gateway}"
            ;;
        cleanup)
            cleanup
            ;;
        cleanup-remote)
            check_prerequisites
            cleanup_remote
            ;;
        help|--help|-h|"")
            usage
            ;;
        *)
            print_error "Unknown command: $cmd"
            usage
            exit 1
            ;;
    esac
}

main "$@"
