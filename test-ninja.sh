#!/bin/bash
set -e

echo "=== Testing OpenSSL Ninja Build Generator ==="

# Check if ninja is available
if ! command -v ninja &> /dev/null; then
    echo "Installing ninja..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y ninja-build
    elif command -v brew &> /dev/null; then
        brew install ninja
    else
        echo "Please install ninja manually: https://ninja-build.org/"
        exit 1
    fi
fi

echo "Ninja version: $(ninja --version)"

# Test 1: Configure with Ninja format
echo "=== Test 1: Configure with Ninja format ==="
perl Configure linux-x86_64 --format=ninja --strict-warnings

if [ -f "build.ninja" ]; then
    echo "✅ build.ninja generated successfully"
    echo "First 10 lines of build.ninja:"
    head -10 build.ninja
else
    echo "❌ build.ninja not generated"
    exit 1
fi

# Test 2: Build with Ninja
echo "=== Test 2: Build with Ninja ==="
ninja -j$(nproc)

if [ -f "apps/openssl" ]; then
    echo "✅ Build completed successfully"
    echo "OpenSSL version: $(./apps/openssl version)"
else
    echo "❌ Build failed"
    exit 1
fi

# Test 3: Run tests
echo "=== Test 3: Run tests ==="
ninja test

echo "✅ Tests completed successfully"

# Test 4: Check for compile_commands.json
echo "=== Test 4: Check for compile_commands.json ==="
if [ -f "compile_commands.json" ]; then
    echo "✅ compile_commands.json generated"
    echo "Number of compile commands: $(jq '. | length' compile_commands.json)"
else
    echo "⚠️ compile_commands.json not found (may be expected for some configurations)"
fi

# Test 5: Test install target
echo "=== Test 5: Test install target ==="
ninja install DESTDIR=./test-install

if [ -d "test-install/usr/local" ]; then
    echo "✅ Install completed successfully"
    ls -la test-install/usr/local/
else
    echo "❌ Install failed"
    exit 1
fi

# Test 6: Compare with Makefile (if available)
echo "=== Test 6: Compare with Makefile ==="
if [ -f "Makefile" ]; then
    echo "⚠️ Makefile exists alongside build.ninja (this is expected)"
else
    echo "✅ No Makefile generated (correct for --format=ninja)"
fi

# Test 7: Test invalid format
echo "=== Test 7: Test invalid format ==="
if perl Configure linux-x86_64 --format=invalid 2>&1 | grep -q "Unknown build format"; then
    echo "✅ Invalid format properly rejected"
else
    echo "❌ Invalid format not rejected"
    exit 1
fi

# Test 8: Test default behavior (unchanged)
echo "=== Test 8: Test default behavior ==="
rm -f build.ninja Makefile
perl Configure linux-x86_64 --strict-warnings

if [ -f "Makefile" ] && [ ! -f "build.ninja" ]; then
    echo "✅ Default Makefile generation still works"
else
    echo "❌ Default behavior changed"
    exit 1
fi

echo ""
echo "🎉 All Ninja build tests passed!"
echo ""
echo "Summary:"
echo "- ✅ Ninja format configuration works"
echo "- ✅ Build with Ninja succeeds"
echo "- ✅ Tests pass with Ninja"
echo "- ✅ Install target works"
echo "- ✅ Invalid format rejected"
echo "- ✅ Default Makefile behavior unchanged"
echo ""
echo "The Ninja build generator is working correctly!"
