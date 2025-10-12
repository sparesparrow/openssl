#!/bin/bash
# Build script following ngapy-dev patterns
# Usage: ./build.sh [options]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="${PROJECT_ROOT}/build"
CONAN_PROFILE="${PROJECT_ROOT}/conan-profiles/default.profile"

# Default values
BUILD_TYPE="Release"
ENABLE_TESTS="True"
ENABLE_DOCS="False"
CLEAN_BUILD="False"
VERBOSE="False"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
Build script for project following ngapy-dev patterns

Usage: $0 [OPTIONS]

Options:
    -h, --help              Show this help message
    -t, --type TYPE         Build type (Debug, Release, RelWithDebInfo, MinSizeRel) [default: Release]
    --no-tests              Disable tests
    --docs                  Enable documentation build
    --clean                 Clean build directory before building
    -v, --verbose           Verbose output
    --profile PROFILE       Conan profile to use [default: default.profile]

Examples:
    $0                      # Build with default settings
    $0 --type Debug         # Build in Debug mode
    $0 --clean --docs       # Clean build with documentation
    $0 --no-tests -v        # Build without tests, verbose output

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        --no-tests)
            ENABLE_TESTS="False"
            shift
            ;;
        --docs)
            ENABLE_DOCS="True"
            shift
            ;;
        --clean)
            CLEAN_BUILD="True"
            shift
            ;;
        -v|--verbose)
            VERBOSE="True"
            shift
            ;;
        --profile)
            CONAN_PROFILE="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate build type
case $BUILD_TYPE in
    Debug|Release|RelWithDebInfo|MinSizeRel)
        ;;
    *)
        log_error "Invalid build type: $BUILD_TYPE"
        exit 1
        ;;
esac

log_info "Starting build process..."
log_info "Project root: $PROJECT_ROOT"
log_info "Build type: $BUILD_TYPE"
log_info "Enable tests: $ENABLE_TESTS"
log_info "Enable docs: $ENABLE_DOCS"
log_info "Clean build: $CLEAN_BUILD"
log_info "Verbose: $VERBOSE"

# Check if conanfile.py exists
if [[ ! -f "$PROJECT_ROOT/conanfile.py" ]]; then
    log_error "conanfile.py not found in project root"
    exit 1
fi

# Clean build directory if requested
if [[ "$CLEAN_BUILD" == "True" ]]; then
    log_info "Cleaning build directory..."
    rm -rf "$BUILD_DIR"
fi

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Set up Conan
log_info "Setting up Conan..."
if [[ -f "$CONAN_PROFILE" ]]; then
    log_info "Using Conan profile: $CONAN_PROFILE"
    CONAN_PROFILE_ARG="--profile:build=$CONAN_PROFILE --profile:host=$CONAN_PROFILE"
else
    log_warning "Conan profile not found: $CONAN_PROFILE"
    CONAN_PROFILE_ARG=""
fi

# Install dependencies
log_info "Installing dependencies..."
conan install "$PROJECT_ROOT" \
    $CONAN_PROFILE_ARG \
    --build=missing \
    --settings=build_type="$BUILD_TYPE" \
    --options=enable_tests="$ENABLE_TESTS" \
    --options=enable_docs="$ENABLE_DOCS"

# Generate build files
log_info "Generating build files..."
conan generate cmake "$PROJECT_ROOT"

# Configure CMake
log_info "Configuring CMake..."
CMAKE_ARGS=(
    -DCMAKE_BUILD_TYPE="$BUILD_TYPE"
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
)

if [[ "$VERBOSE" == "True" ]]; then
    CMAKE_ARGS+=(-DCMAKE_VERBOSE_MAKEFILE=ON)
fi

cmake "${CMAKE_ARGS[@]}" "$PROJECT_ROOT"

# Build
log_info "Building project..."
if [[ "$VERBOSE" == "True" ]]; then
    make VERBOSE=1 -j$(nproc)
else
    make -j$(nproc)
fi

# Run tests if enabled
if [[ "$ENABLE_TESTS" == "True" ]]; then
    log_info "Running tests..."
    if [[ -f "CTestTestfile.cmake" ]]; then
        ctest --output-on-failure
        log_success "Tests completed successfully"
    else
        log_warning "No tests found"
    fi
fi

# Build documentation if enabled
if [[ "$ENABLE_DOCS" == "True" ]]; then
    log_info "Building documentation..."
    if [[ -d "docs" ]]; then
        make docs
        log_success "Documentation built successfully"
    else
        log_warning "No documentation found"
    fi
fi

log_success "Build completed successfully!"
log_info "Build artifacts are in: $BUILD_DIR"