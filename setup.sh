#!/bin/bash

# Online Sharia Academy - Automated Setup Script
# This script sets up both backend and frontend for development

set -e  # Exit on any error

echo "🕌 Online Sharia Academy - Automated Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d. -f1-2)
    if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
        print_error "Python $PYTHON_VERSION is too old. Please upgrade to Python 3.9 or higher."
        exit 1
    fi
    print_success "Python $PYTHON_VERSION found"

    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi

    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d. -f1)
    if [[ $NODE_VERSION -lt 18 ]]; then
        print_error "Node.js v$NODE_VERSION is too old. Please upgrade to Node.js 18 or higher."
        exit 1
    fi
    print_success "Node.js $(node --version) found"

    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed."
        exit 1
    fi
    print_success "npm $(npm --version) found"
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."

    cd osa-backend

    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv

    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt

    # Run database migrations
    print_status "Setting up database..."
    PYTHONPATH=. alembic upgrade head

    # Create sample data
    print_status "Creating sample data..."
    python create_sample_content.py
    python create_test_user.py

    print_success "Backend setup complete!"
    cd ..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."

    cd osa-frontend

    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install

    print_success "Frontend setup complete!"
    cd ..
}

# Start services
start_services() {
    print_status "Starting services..."

    # Start backend
    print_status "Starting backend server..."
    cd osa-backend
    source venv/bin/activate
    PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
    BACKEND_PID=$!
    cd ..

    # Wait a moment for backend to start
    sleep 3

    # Start frontend
    print_status "Starting frontend server..."
    cd osa-frontend
    npm start &
    FRONTEND_PID=$!
    cd ..

    print_success "Services started!"
    echo ""
    echo "🎉 Setup complete! Access your application at:"
    echo "   Frontend: http://localhost:4200"
    echo "   Backend API: http://localhost:8001"
    echo "   API Docs: http://localhost:8001/docs"
    echo ""
    echo "Test credentials:"
    echo "   Email: test@test.com"
    echo "   Password: pass123"
    echo ""
    print_warning "Press Ctrl+C to stop all services"

    # Wait for services
    wait $BACKEND_PID $FRONTEND_PID
}

# Cleanup function
cleanup() {
    print_warning "Stopping services..."
    kill 0
    exit 0
}

# Main execution
main() {
    # Set trap for cleanup
    trap cleanup SIGINT SIGTERM

    print_status "Starting Online Sharia Academy setup..."

    check_prerequisites
    setup_backend
    setup_frontend
    start_services
}

# Run main function
main "$@"