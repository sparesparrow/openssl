#!/bin/bash
# Setup script for vcpkg integration with OpenSSL tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default vcpkg installation directory
VCPKG_ROOT="${VCPKG_ROOT:-$HOME/vcpkg}"

echo -e "${GREEN}Setting up vcpkg integration for OpenSSL tools...${NC}"

# Check if vcpkg is already installed
if [ -d "$VCPKG_ROOT" ] && [ -f "$VCPKG_ROOT/vcpkg" ]; then
    echo -e "${GREEN}✅ vcpkg found at: $VCPKG_ROOT${NC}"
else
    echo -e "${YELLOW}⚠️ vcpkg not found. Installing vcpkg...${NC}"
    
    # Clone vcpkg
    git clone https://github.com/Microsoft/vcpkg.git "$VCPKG_ROOT"
    
    # Bootstrap vcpkg
    cd "$VCPKG_ROOT"
    ./bootstrap-vcpkg.sh
    
    echo -e "${GREEN}✅ vcpkg installed successfully${NC}"
fi

# Set environment variables
export VCPKG_ROOT="$VCPKG_ROOT"
export VCPKG_DEFAULT_TRIPLET="${VCPKG_DEFAULT_TRIPLET:-x64-linux}"
export CMAKE_TOOLCHAIN_FILE="$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake"

echo -e "${GREEN}Environment variables set:${NC}"
echo "  VCPKG_ROOT=$VCPKG_ROOT"
echo "  VCPKG_DEFAULT_TRIPLET=$VCPKG_DEFAULT_TRIPLET"
echo "  CMAKE_TOOLCHAIN_FILE=$CMAKE_TOOLCHAIN_FILE"

# Install OpenSSL dependencies
echo -e "${GREEN}Installing OpenSSL dependencies...${NC}"
cd "$VCPKG_ROOT"

# Install basic dependencies
./vcpkg install openssl[core,tools] zlib

# Install FIPS dependencies if requested
if [ "$1" = "--fips" ]; then
    echo -e "${GREEN}Installing FIPS dependencies...${NC}"
    ./vcpkg install openssl[fips]
fi

echo -e "${GREEN}✅ vcpkg setup complete!${NC}"
echo -e "${YELLOW}To use vcpkg with CMake, add this to your CMakeLists.txt:${NC}"
echo "  set(CMAKE_TOOLCHAIN_FILE \"$CMAKE_TOOLCHAIN_FILE\")"