#!/bin/bash

# SaveVia Backend Restart Script
# Compatible with macOS default bash (no associative arrays)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Service startup order
SERVICE_ORDER="eureka gateway card optimizer user"

# Get service directory
get_service_dir() {
    case $1 in
        eureka)    echo "savevia-eureka" ;;
        gateway)   echo "savevia-gateway" ;;
        user)      echo "savevia-user" ;;
        card)      echo "savevia-card" ;;
        optimizer) echo "savevia-optimizer" ;;
        *)         echo "" ;;
    esac
}

# Get service port
get_service_port() {
    case $1 in
        eureka)    echo "8761" ;;
        gateway)   echo "8080" ;;
        user)      echo "8081" ;;
        card)      echo "8082" ;;
        optimizer) echo "8083" ;;
        *)         echo "" ;;
    esac
}

print_menu() {
    echo "=========================================="
    echo "  SaveVia Backend Restart Menu"
    echo "=========================================="
    echo ""
    echo "  1) Eureka     (Service Discovery - :8761)"
    echo "  2) Gateway    (API Gateway - :8080)"
    echo "  3) User       (User Service - :8081)"
    echo "  4) Card       (Card Service - :8082)"
    echo "  5) Optimizer  (Optimizer Service - :8083)"
    echo ""
    echo "  a) All services (in order)"
    echo "  s) Show running services"
    echo "  k) Kill all services"
    echo "  q) Quit"
    echo ""
    echo "=========================================="
}

stop_service() {
    local service=$1
    local dir=$(get_service_dir $service)
    local port=$(get_service_port $service)

    echo "Stopping $service (port $port)..."
    # Kill Java process on port
    lsof -ti:$port | xargs kill -9 2>/dev/null
    # Also kill any maven process for this service
    pkill -9 -f "spring-boot:run.*$dir" 2>/dev/null
    sleep 2
}

start_service() {
    local service=$1
    local dir=$(get_service_dir $service)
    local port=$(get_service_port $service)

    echo "Starting $service..."
    echo "Directory: $SCRIPT_DIR/$dir"

    if [ ! -d "$SCRIPT_DIR/$dir" ]; then
        echo "ERROR: Directory does not exist!"
        return 1
    fi

    cd "$SCRIPT_DIR/$dir" || { echo "Failed to cd"; return 1; }
    echo "Current dir: $(pwd)"

    # Always rebuild to pick up code changes
    echo "Building $service..."
    mvn clean compile -DskipTests
    local build_result=$?

    if [ $build_result -ne 0 ]; then
        echo "Build failed for $service! (exit code: $build_result)"
        return 1
    fi
    echo "Build successful!"

    # Run the service
    mvn spring-boot:run &

    # Wait for service to start
    echo "Waiting for $service to start on port $port..."
    local max_wait=60
    local waited=0
    while ! lsof -ti:$port > /dev/null 2>&1; do
        sleep 2
        waited=$((waited + 2))
        if [ $waited -ge $max_wait ]; then
            echo "Warning: $service may not have started properly"
            break
        fi
    done

    if lsof -ti:$port > /dev/null 2>&1; then
        echo "$service started successfully on port $port"
    fi
}

restart_service() {
    local service=$1
    stop_service $service
    start_service $service
}

show_running_services() {
    echo ""
    echo "Running Services:"
    echo "-----------------"
    for service in $SERVICE_ORDER; do
        local port=$(get_service_port $service)
        if lsof -ti:$port > /dev/null 2>&1; then
            echo "  [RUNNING] $service (port $port)"
        else
            echo "  [STOPPED] $service (port $port)"
        fi
    done
    echo ""
}

kill_all_services() {
    echo "Stopping all services..."
    for service in $SERVICE_ORDER; do
        stop_service $service
    done
    echo "All services stopped."
}

start_all_services() {
    echo "Starting all services in order..."
    echo ""

    for service in $SERVICE_ORDER; do
        restart_service $service
        echo ""

        # Extra wait for eureka to be fully ready
        if [ "$service" = "eureka" ]; then
            echo "Waiting for Eureka to be fully ready..."
            sleep 10
        fi
    done

    echo "All services started!"
    show_running_services
}

# Main loop
while true; do
    print_menu
    read -p "Enter choice: " choice

    case $choice in
        1) restart_service "eureka" ;;
        2) restart_service "gateway" ;;
        3) restart_service "user" ;;
        4) restart_service "card" ;;
        5) restart_service "optimizer" ;;
        a|A) start_all_services ;;
        s|S) show_running_services ;;
        k|K) kill_all_services ;;
        q|Q) echo "Bye!"; exit 0 ;;
        *) echo "Invalid choice" ;;
    esac

    echo ""
    read -p "Press Enter to continue..."
done
