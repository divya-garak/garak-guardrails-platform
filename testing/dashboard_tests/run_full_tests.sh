#!/bin/bash

# Full Test Runner for NeMo Guardrails Dashboard Tests
# This script manages the complete lifecycle of services and testing

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.test.yml"
TEST_TIMEOUT=${TEST_TIMEOUT:-300}  # 5 minutes default
MAX_RETRIES=${MAX_RETRIES:-3}
HEALTH_CHECK_INTERVAL=10

# Service endpoints for health checks
declare -A SERVICES=(
    ["nemo-main"]="http://localhost:8000"
    ["nemo-comprehensive"]="http://localhost:8004"
    ["jailbreak-service"]="http://localhost:1337"
    ["presidio-service"]="http://localhost:5001"
    ["content-safety"]="http://localhost:5002"
    ["llama-guard"]="http://localhost:8001"
    ["factcheck-service"]="http://localhost:5000"
)

print_header() {
    echo -e "${BLUE}===========================================${NC}"
    echo -e "${BLUE}  NeMo Guardrails Dashboard Test Runner  ${NC}"
    echo -e "${BLUE}===========================================${NC}"
    echo ""
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cleanup_services() {
    print_status "Cleaning up existing services..."
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans 2>/dev/null || true
    
    # Kill any processes using the test ports
    for port in 8000 8001 8004 1337 5000 5001 5002; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            print_warning "Killing process on port $port"
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
}

check_requirements() {
    print_status "Checking requirements..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if docker-compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "docker-compose is not installed. Please install it and try again."
        exit 1
    fi
    
    # Check if pytest is available
    if ! python3 -m pytest --version >/dev/null 2>&1; then
        print_error "pytest is not available. Please install it with: pip install pytest"
        exit 1
    fi
    
    print_status "All requirements satisfied ✓"
}

start_services() {
    print_status "Starting all services with Docker Compose..."
    
    # Build and start services
    docker-compose -f "$COMPOSE_FILE" build --parallel
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_status "Services started. Waiting for health checks..."
}

wait_for_service() {
    local service_name=$1
    local service_url=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Checking health of $service_name at $service_url"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$service_url/health" >/dev/null 2>&1 || \
           curl -f -s "$service_url/" >/dev/null 2>&1; then
            print_status "$service_name is healthy ✓"
            return 0
        fi
        
        echo -n "."
        sleep $HEALTH_CHECK_INTERVAL
        ((attempt++))
    done
    
    print_warning "$service_name failed health check after $max_attempts attempts"
    return 1
}

wait_for_all_services() {
    print_status "Performing health checks on all services..."
    local failed_services=()
    
    for service_name in "${!SERVICES[@]}"; do
        service_url="${SERVICES[$service_name]}"
        if ! wait_for_service "$service_name" "$service_url"; then
            failed_services+=("$service_name")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_status "All services are healthy! ✓"
        return 0
    else
        print_warning "The following services failed health checks: ${failed_services[*]}"
        print_status "Continuing with available services..."
        return 0
    fi
}

run_tests() {
    print_status "Running pytest test suite..."
    
    local test_args=("$@")
    if [ ${#test_args[@]} -eq 0 ]; then
        test_args=("-v" "--tb=short" "--maxfail=5")
    fi
    
    # Set test environment variables
    export PYTEST_TIMEOUT=$TEST_TIMEOUT
    
    # Run the tests
    if python3 -m pytest . "${test_args[@]}"; then
        print_status "All tests completed successfully! ✓"
        return 0
    else
        print_error "Some tests failed. Check the output above for details."
        return 1
    fi
}

show_service_logs() {
    print_status "Showing service logs (last 50 lines each):"
    echo ""
    
    for service_name in "${!SERVICES[@]}"; do
        echo -e "${BLUE}=== $service_name logs ===${NC}"
        docker-compose -f "$COMPOSE_FILE" logs --tail=50 "$service_name" 2>/dev/null || \
            echo "No logs available for $service_name"
        echo ""
    done
}

main() {
    local test_args=("$@")
    
    print_header
    
    # Parse command line arguments
    local cleanup_only=false
    local logs_only=false
    local skip_cleanup=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cleanup-only)
                cleanup_only=true
                shift
                ;;
            --logs-only)
                logs_only=true
                shift
                ;;
            --skip-cleanup)
                skip_cleanup=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS] [PYTEST_ARGS...]"
                echo ""
                echo "Options:"
                echo "  --cleanup-only    Only cleanup services and exit"
                echo "  --logs-only       Only show service logs and exit"
                echo "  --skip-cleanup    Skip initial cleanup"
                echo "  --help, -h        Show this help message"
                echo ""
                echo "Environment variables:"
                echo "  TEST_TIMEOUT      Test timeout in seconds (default: 300)"
                echo "  MAX_RETRIES       Maximum retries for health checks (default: 3)"
                echo ""
                echo "Examples:"
                echo "  $0                           # Run all tests"
                echo "  $0 test_smoke.py             # Run specific test file"
                echo "  $0 -k 'docker'               # Run tests matching pattern"
                echo "  $0 --cleanup-only            # Just cleanup services"
                exit 0
                ;;
            *)
                break
                ;;
        esac
    done
    
    if [ "$logs_only" = true ]; then
        show_service_logs
        exit 0
    fi
    
    # Cleanup existing services unless skipped
    if [ "$skip_cleanup" != true ]; then
        cleanup_services
    fi
    
    if [ "$cleanup_only" = true ]; then
        print_status "Cleanup completed."
        exit 0
    fi
    
    # Check requirements
    check_requirements
    
    # Start services
    start_services
    
    # Wait for services to be ready
    wait_for_all_services
    
    # Run tests
    local test_exit_code=0
    if ! run_tests "$@"; then
        test_exit_code=1
    fi
    
    # Show logs if tests failed
    if [ $test_exit_code -ne 0 ]; then
        print_status "Showing service logs due to test failures:"
        show_service_logs
    fi
    
    # Cleanup services
    print_status "Cleaning up services..."
    cleanup_services
    
    if [ $test_exit_code -eq 0 ]; then
        print_status "✅ All tests passed! Dashboard test suite completed successfully."
    else
        print_error "❌ Some tests failed. See output above for details."
    fi
    
    exit $test_exit_code
}

# Run main function with all arguments
main "$@"