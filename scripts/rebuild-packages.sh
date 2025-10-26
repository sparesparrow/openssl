#!/bin/bash
# rebuild-openssl-packages.sh - Clean rebuild of all packages

set -e

echo "🔨 OpenSSL Package Rebuild"
echo "==========================="

cd ~/projects/openssl-devenv

# 1. openssl-profiles (foundation layer)
echo -e "\n📦 Building openssl-profiles..."
cd openssl-profiles
conan create . --build=missing
cd ..

# 2. openssl-tools (tooling layer)
echo -e "\n🔧 Building openssl-tools..."
cd openssl-tools
conan create . --build=missing
cd ..

# 3. openssl (main package)
echo -e "\n🔐 Building openssl..."
cd openssl
conan create . --build=missing
cd ..

echo -e "\n✅ All packages rebuilt successfully!"

# 4. Verify dependency graph
echo -e "\n📊 Dependency graph:"
conan graph info ~/projects/openssl-devenv/openssl --format=compact

# 5. Test consumer integration
echo -e "\n🧪 Testing libcurl consumer..."
cd libcurl
conan install . --build=missing
cd ..

echo -e "\n🎉 Rebuild and verification complete!"