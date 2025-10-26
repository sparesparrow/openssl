#!/bin/bash
# verify-clean-rebuild.sh

echo "🔍 Verification Steps"
echo "===================="

# 1. Check cache is clean
echo -e "\n1️⃣ Cache status:"
conan list "openssl*" --format=compact

# 2. Rebuild openssl-profiles
echo -e "\n2️⃣ Building openssl-profiles..."
cd ~/projects/openssl-devenv/openssl-profiles
conan create . --build=missing
PROFILES_REF=$(conan list "openssl-profiles/*" --format=compact | head -1)
echo "✓ Created: $PROFILES_REF"

# 3. Rebuild openssl-tools
echo -e "\n3️⃣ Building openssl-tools..."
cd ~/projects/openssl-devenv/openssl-tools
conan create . --build=missing
TOOLS_REF=$(conan list "openssl-tools/*" --format=compact | head -1)
echo "✓ Created: $TOOLS_REF"

# 4. Rebuild openssl
echo -e "\n4️⃣ Building openssl..."
cd ~/projects/openssl-devenv/openssl
conan create . --build=missing
OPENSSL_REF=$(conan list "openssl/*" --format=compact | head -1)
echo "✓ Created: $OPENSSL_REF"

# 5. Verify package integrity
echo -e "\n5️⃣ Package integrity check:"
PACKAGE_PATH=$(conan cache path "$OPENSSL_REF" | head -1)
echo "Package location: $PACKAGE_PATH"

# Check for libraries
if [ -f "$PACKAGE_PATH/lib/libcrypto.so" ] || [ -f "$PACKAGE_PATH/lib/libcrypto.a" ]; then
    echo "✅ libcrypto found"
else
    echo "❌ libcrypto MISSING!"
    exit 1
fi

if [ -f "$PACKAGE_PATH/lib/libssl.so" ] || [ -f "$PACKAGE_PATH/lib/libssl.a" ]; then
    echo "✅ libssl found"
else
    echo "❌ libssl MISSING!"
    exit 1
fi

# Check for binaries
if [ -f "$PACKAGE_PATH/bin/openssl" ]; then
    echo "✅ openssl binary found"
    $PACKAGE_PATH/bin/openssl version
else
    echo "❌ openssl binary MISSING!"
    exit 1
fi

# 6. Test downstream consumer
echo -e "\n6️⃣ Testing libcurl consumer:"
cd ~/projects/openssl-devenv/libcurl
conan install . --build=missing
if [ $? -eq 0 ]; then
    echo "✅ libcurl integration successful"
else
    echo "❌ libcurl integration FAILED!"
    exit 1
fi

echo -e "\n🎉 All verification checks passed!"