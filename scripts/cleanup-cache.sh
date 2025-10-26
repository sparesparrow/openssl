#!/bin/bash
# cleanup-openssl-cache.sh - Remove stale OpenSSL builds

set -e

echo "🧹 OpenSSL Conan Cache Cleanup"
echo "================================"

# 1. Show current cache size
echo -e "\n📊 Current cache size:"
du -sh ~/.conan2/

# 2. List all OpenSSL packages
echo -e "\n📦 Installed OpenSSL packages:"
conan list "openssl*" --format=compact

# 3. Remove all OpenSSL package builds (keeps recipes)
echo -e "\n🗑️  Removing OpenSSL package binaries..."
conan remove "openssl/*" -c --confirm

# 4. Remove all openssl-profiles builds
echo -e "\n🗑️  Removing openssl-profiles binaries..."
conan remove "openssl-profiles/*" -c --confirm

# 5. Remove all openssl-tools builds
echo -e "\n🗑️  Removing openssl-tools binaries..."
conan remove "openssl-tools/*" -c --confirm

# 6. Clean build folder artifacts
echo -e "\n🗑️  Cleaning build folders..."
find ~/.conan2/p/b/ -type d -name "opens*" -exec rm -rf {} + 2>/dev/null || true

# 7. Show new cache size
echo -e "\n📊 Cache size after cleanup:"
du -sh ~/.conan2/

echo -e "\n✅ Cleanup complete!"