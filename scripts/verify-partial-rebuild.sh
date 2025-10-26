#!/bin/bash
# verify-partial-rebuild.sh - Verify packages that have been built

echo "🔍 Partial Verification Steps"
echo "============================="

# 1. Check cache status
echo -e "\n1️⃣ Cache status:"
conan list "openssl*" --format=compact

# 2. Verify openssl-profiles
echo -e "\n2️⃣ Verifying openssl-profiles..."
PROFILES_REF=$(conan list "openssl-profiles/*" --format=compact | grep -v "Local Cache" | head -1 | xargs)
if [ -n "$PROFILES_REF" ]; then
    echo "✓ Found: $PROFILES_REF"
    PROFILES_PATH=$(conan cache path "$PROFILES_REF" | head -1)
    echo "Package location: $PROFILES_PATH"
    
    # Check for profiles
    if [ -d "$PROFILES_PATH/profiles" ]; then
        echo "✅ Profiles directory found"
        ls -la "$PROFILES_PATH/profiles" | head -5
    else
        echo "❌ Profiles directory MISSING!"
    fi
    
    # Check for FIPS data
    if [ -d "$PROFILES_PATH/fips" ]; then
        echo "✅ FIPS data directory found"
        ls -la "$PROFILES_PATH/fips" | head -5
    else
        echo "❌ FIPS data directory MISSING!"
    fi
else
    echo "❌ No openssl-profiles found!"
fi

# 3. Verify openssl-tools
echo -e "\n3️⃣ Verifying openssl-tools..."
TOOLS_REF=$(conan list "openssl-tools/*" --format=compact | grep -v "Local Cache" | head -1 | xargs)
if [ -n "$TOOLS_REF" ]; then
    echo "✓ Found: $TOOLS_REF"
    TOOLS_PATH=$(conan cache path "$TOOLS_REF" | head -1)
    echo "Package location: $TOOLS_PATH"
    
    # Check for Python modules
    if [ -d "$TOOLS_PATH/openssl_tools" ]; then
        echo "✅ openssl_tools Python module found"
        ls -la "$TOOLS_PATH/openssl_tools" | head -5
    else
        echo "❌ openssl_tools Python module MISSING!"
    fi
    
    # Check for scripts
    if [ -d "$TOOLS_PATH/scripts" ]; then
        echo "✅ Scripts directory found"
        ls -la "$TOOLS_PATH/scripts" | head -5
    else
        echo "❌ Scripts directory MISSING!"
    fi
else
    echo "❌ No openssl-tools found!"
fi

# 4. Check openssl build status
echo -e "\n4️⃣ Checking openssl build status..."
OPENSSL_REF=$(conan list "openssl/*" --format=compact | grep -v "Local Cache" | head -1 | xargs)
if [ -n "$OPENSSL_REF" ]; then
    echo "✓ Found: $OPENSSL_REF"
    OPENSSL_PATH=$(conan cache path "$OPENSSL_REF" | head -1)
    echo "Package location: $OPENSSL_PATH"
    
    # Check if build is complete
    if [ -f "$OPENSSL_PATH/lib/libcrypto.so" ] || [ -f "$OPENSSL_PATH/lib/libcrypto.a" ]; then
        echo "✅ libcrypto found - build appears complete"
        if [ -f "$OPENSSL_PATH/bin/openssl" ]; then
            echo "✅ openssl binary found"
            $OPENSSL_PATH/bin/openssl version 2>/dev/null || echo "⚠️ Binary exists but may not be executable"
        else
            echo "❌ openssl binary MISSING!"
        fi
    else
        echo "⏳ libcrypto not found - build may still be in progress"
        echo "Build processes running: $(ps aux | grep -E '(conan|make)' | grep -v grep | wc -l)"
    fi
else
    echo "❌ No openssl package found!"
fi

# 5. Cache size summary
echo -e "\n5️⃣ Cache size summary:"
du -sh ~/.conan2/

echo -e "\n🎉 Partial verification complete!"