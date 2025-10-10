#!/bin/bash
# Integration test trigger script

set -e

TOOLS_REPO="sparesparrow/openssl-tools"
OPENSSL_REPO="sparesparrow/openssl" 
OPENSSL_REF="${1:-master}"

echo "🧪 Testing cross-repository integration"
echo "OpenSSL Repository: $OPENSSL_REPO"
echo "OpenSSL Reference: $OPENSSL_REF"
echo "Tools Repository: $TOOLS_REPO"

# Test 1: Trigger from OpenSSL to Tools
echo ""
echo "🔄 Test 1: Repository Dispatch Trigger"
gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  "/repos/$TOOLS_REPO/dispatches" \
  -f event_type='openssl-build-triggered' \
  -f client_payload='{
    "source_repo": "'$OPENSSL_REPO'",
    "ref": "'$OPENSSL_REF'",
    "sha": "integration-test-'$(date +%s)'",
    "build_scope": "minimal",
    "trigger_event": "integration_test",
    "author": "integration-script",
    "workflow_run_id": "test",
    "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'

echo "✅ Repository dispatch sent successfully"

# Test 2: Check workflow was triggered
echo ""
echo "⏳ Test 2: Checking workflow trigger..."
sleep 10

WORKFLOW_RUNS=$(gh api "/repos/$TOOLS_REPO/actions/runs" --jq '.workflow_runs[] | select(.name=="Basic OpenSSL Integration Test") | select(.created_at > "'$(date -d '1 minute ago' -u +%Y-%m-%dT%H:%M:%SZ)'") | .id')

if [ -n "$WORKFLOW_RUNS" ]; then
  echo "✅ Workflow triggered successfully: $WORKFLOW_RUNS"
else
  echo "❌ No workflow runs found - integration may have failed"
  exit 1
fi

echo ""
echo "🎉 Integration test completed successfully!"
echo "Monitor workflow progress at: https://github.com/$TOOLS_REPO/actions"
