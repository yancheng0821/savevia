#!/bin/bash

# SaveVia Backend Restart Script
# Compatible with macOS default bash (no associative arrays)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load environment variables from .env file
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Loading environment variables from .env..."
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
else
    echo "Warning: .env file not found. Using default values."
fi

# Service startup order
# Gateway should start LAST so all services are registered with Eureka first
SERVICE_ORDER="eureka card optimizer user gateway"

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

    # First, kill the Java process running on the port
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pid" ]; then
        echo "  Killing process $pid on port $port..."
        kill -9 $pid 2>/dev/null
    fi

    # Kill any maven spring-boot:run process for this specific service
    local maven_pid=$(pgrep -f "multiModuleProjectDirectory.*$dir.*spring-boot:run" 2>/dev/null)
    if [ -n "$maven_pid" ]; then
        echo "  Killing maven process $maven_pid..."
        kill -9 $maven_pid 2>/dev/null
    fi

    # Kill any java -jar process for this service
    local jar_pid=$(pgrep -f "java.*$dir.*jar" 2>/dev/null)
    if [ -n "$jar_pid" ]; then
        echo "  Killing jar process $jar_pid..."
        kill -9 $jar_pid 2>/dev/null
    fi

    # Wait for port to be released
    local waited=0
    while lsof -ti:$port > /dev/null 2>&1 && [ $waited -lt 10 ]; do
        sleep 1
        waited=$((waited + 1))
    done

    if lsof -ti:$port > /dev/null 2>&1; then
        echo "  Warning: Port $port still in use after 10s"
    else
        echo "  $service stopped."
    fi
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
    mvn clean package -DskipTests -q
    local build_result=$?

    if [ $build_result -ne 0 ]; then
        echo "Build failed for $service! (exit code: $build_result)"
        return 1
    fi
    echo "Build successful!"

    # Run the packaged jar with nohup to prevent it from being affected by subsequent commands
    local jar_file=$(ls target/*.jar 2>/dev/null | grep -v original | head -1)
    if [ -z "$jar_file" ]; then
        echo "ERROR: No jar file found in target/"
        return 1
    fi
    echo "Running $jar_file..."

    # Create logs directory if not exists
    mkdir -p "$SCRIPT_DIR/logs"

    # Use nohup and redirect output to log file
    nohup java -jar "$jar_file" > "$SCRIPT_DIR/logs/$service.log" 2>&1 &
    local pid=$!
    echo "Started with PID: $pid"

    # Wait for service to start (check port)
    echo "Waiting for $service to start on port $port..."
    local max_wait=90
    local waited=0
    while ! lsof -ti:$port > /dev/null 2>&1; do
        sleep 2
        waited=$((waited + 2))
        if [ $waited -ge $max_wait ]; then
            echo "ERROR: $service failed to start within ${max_wait}s"
            echo "Check log: $SCRIPT_DIR/logs/$service.log"
            tail -20 "$SCRIPT_DIR/logs/$service.log" 2>/dev/null
            return 1
        fi
        # Check if process is still running
        if ! kill -0 $pid 2>/dev/null; then
            echo "ERROR: $service process died unexpectedly"
            echo "Check log: $SCRIPT_DIR/logs/$service.log"
            tail -30 "$SCRIPT_DIR/logs/$service.log" 2>/dev/null
            return 1
        fi
    done

    # Additional health check for services with actuator
    if [ "$service" = "eureka" ]; then
        echo "Verifying Eureka is healthy..."
        local health_waited=0
        while [ $health_waited -lt 30 ]; do
            if curl -s http://localhost:8761/actuator/health 2>/dev/null | grep -q '"status":"UP"'; then
                echo "Eureka health check passed!"
                break
            fi
            sleep 2
            health_waited=$((health_waited + 2))
        done
    fi

    echo "$service started successfully on port $port (PID: $pid)"
}

restart_service() {
    local service=$1

    # Check gateway status before restart
    echo "=== Pre-restart check ==="
    local gw_pid=$(lsof -ti:8080 2>/dev/null)
    if [ -n "$gw_pid" ]; then
        echo "  Gateway is running (PID: $gw_pid)"
    else
        echo "  Gateway is NOT running"
    fi

    stop_service $service

    # Check gateway status after stop
    echo "=== Post-stop check ==="
    gw_pid=$(lsof -ti:8080 2>/dev/null)
    if [ -n "$gw_pid" ]; then
        echo "  Gateway still running (PID: $gw_pid)"
    else
        echo "  WARNING: Gateway stopped unexpectedly!"
    fi

    start_service $service

    # Check gateway status after start
    echo "=== Post-start check ==="
    gw_pid=$(lsof -ti:8080 2>/dev/null)
    if [ -n "$gw_pid" ]; then
        echo "  Gateway is running (PID: $gw_pid)"
    else
        echo "  WARNING: Gateway is NOT running!"
    fi
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
    echo "Order: $SERVICE_ORDER"
    echo ""

    for service in $SERVICE_ORDER; do
        restart_service $service
        local result=$?
        echo ""

        if [ $result -ne 0 ]; then
            echo "ERROR: Failed to start $service. Stopping."
            return 1
        fi

        # Extra wait after eureka to ensure it's accepting registrations
        if [ "$service" = "eureka" ]; then
            echo "Waiting for Eureka to be fully ready for registrations..."
            sleep 15
        fi

        # Wait for services to register with Eureka before starting Gateway
        if [ "$service" = "user" ]; then
            echo "Waiting for all services to register with Eureka..."
            sleep 10
        fi
    done

    echo ""
    echo "=========================================="
    echo "  All services started successfully!"
    echo "=========================================="
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
