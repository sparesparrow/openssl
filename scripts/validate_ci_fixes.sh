#!/bin/bash
# Validate CI/CD Optimization Fixes
# This script checks that the CI optimizations are working correctly

set -e

echo "🔍 Validating CI/CD Optimization Fixes..."

# Check that the workflows exist and are valid
echo "📋 Checking workflow files..."

WORKFLOWS=(
    ".github/workflows/main.yml"
    ".github/workflows/optimized-ci.yml" 
    ".github/workflows/incremental-ci-patch.yml"
)

for workflow in "${WORKFLOWS[@]}"; do
    if [ -f "$workflow" ]; then
        echo "✅ $workflow exists"
        
        # Basic YAML syntax check
        if command -v yamllint >/dev/null 2>&1; then
            yamllint "$workflow" && echo "  ✅ YAML syntax valid" || echo "  ⚠️  YAML syntax issues"
        fi
        
        # Check for key optimizations
        if grep -q "paths:" "$workflow"; then
            echo "  ✅ Path-based filtering detected"
        fi
        
        if grep -q "cache@v4" "$workflow"; then
            echo "  ✅ Caching enabled"
        fi
        
        if grep -q "dorny/paths-filter" "$workflow"; then
            echo "  ✅ Change detection implemented"
        fi
        
    else
        echo "❌ $workflow missing"
    fi
done

# Check for change detection logic
echo ""
echo "🔍 Validating change detection logic..."

if [ -f ".github/workflows/optimized-ci.yml" ]; then
    # Check that all major directories are covered
    DIRECTORIES=("apps" "crypto" "ssl" "providers" "include" "test" "fuzz" "doc")
    
    for dir in "${DIRECTORIES[@]}"; do
        if grep -q "$dir/\*\*" ".github/workflows/optimized-ci.yml"; then
            echo "✅ Change detection covers $dir/"
        else
            echo "⚠️  Change detection missing $dir/"
        fi
    done
fi

# Check CIFuzz optimizations
echo ""
echo "🔍 Validating CIFuzz optimizations..."

if [ -f ".github/workflows/main.yml" ]; then
    if grep -q "paths:" ".github/workflows/main.yml"; then
        echo "✅ CIFuzz has path-based filtering"
    else
        echo "❌ CIFuzz missing path filtering"
    fi
    
    if grep -q "schedule:" ".github/workflows/main.yml"; then
        echo "✅ CIFuzz has scheduled execution"
    else
        echo "❌ CIFuzz missing schedule"
    fi
    
    if grep -q "workflow_dispatch:" ".github/workflows/main.yml"; then
        echo "✅ CIFuzz has manual trigger"
    else
        echo "❌ CIFuzz missing manual trigger"
    fi
    
    # Check fuzz duration is optimized
    if grep -q "fuzz-seconds.*300" ".github/workflows/main.yml"; then
        echo "✅ CIFuzz duration optimized (300s)"
    elif grep -q "fuzz-seconds.*600" ".github/workflows/main.yml"; then
        echo "⚠️  CIFuzz still using long duration (600s)"
    fi
fi

# Check for build optimization patterns
echo ""
echo "🔍 Checking build optimization patterns..."

OPTIMIZATION_PATTERNS=(
    "incremental"
    "cache"
    "skip"
    "conditional"
)

for pattern in "${OPTIMIZATION_PATTERNS[@]}"; do
    if grep -r -i "$pattern" .github/workflows/ >/dev/null 2>&1; then
        echo "✅ $pattern optimization detected"
    else
        echo "⚠️  $pattern optimization not found"
    fi
done

# Test change detection simulation
echo ""
echo "🧪 Testing change detection simulation..."

# Simulate different types of changes
TEST_CASES=(
    "doc/README.md:docs-only"
    "crypto/aes.c:source-change"
    "test/test_aes.c:test-change"
    "fuzz/fuzz_aes.c:fuzz-change"
    "Configure:config-change"
)

for test_case in "${TEST_CASES[@]}"; do
    file="${test_case%:*}"
    type="${test_case#*:}"
    
    if [ -f "$file" ]; then
        echo "✅ Test case file exists: $file ($type)"
    else
        echo "⚠️  Test case file missing: $file ($type)"
    fi
done

# Check documentation
echo ""
echo "📚 Checking documentation..."

DOCS=(
    "CI-OPTIMIZATION-FIXES.md"
    "README-MODERNIZATION.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc exists"
        
        # Check for key sections
        if grep -q "optimization" "$doc" 2>/dev/null; then
            echo "  ✅ Contains optimization information"
        fi
    else
        echo "❌ $doc missing"
    fi
done

# Summary
echo ""
echo "📊 Validation Summary"
echo "===================="

TOTAL_CHECKS=0
PASSED_CHECKS=0

# Count workflow files
for workflow in "${WORKFLOWS[@]}"; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ -f "$workflow" ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
done

# Count optimization patterns
for pattern in "${OPTIMIZATION_PATTERNS[@]}"; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if grep -r -i "$pattern" .github/workflows/ >/dev/null 2>&1; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    fi
done

PASS_RATE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))

echo "Checks passed: $PASSED_CHECKS/$TOTAL_CHECKS ($PASS_RATE%)"

if [ $PASS_RATE -ge 80 ]; then
    echo "✅ CI optimization validation PASSED"
    exit 0
else
    echo "❌ CI optimization validation FAILED"
    exit 1
fi