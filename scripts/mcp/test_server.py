#!/usr/bin/env python3
"""
Test script for MCP GitHub Workflow Fixer Server
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from github_workflow_fixer import GitHubWorkflowFixer

async def test_server():
    """Test the MCP server functionality"""

    # Use environment variable for token
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set it with: export GITHUB_TOKEN='your_token_here'")
        return False

    # Test repository - you can change this to your own repo
    test_repo = "sparesparrow/openssl-tools"

    print(f"🧪 Testing MCP GitHub Workflow Fixer Server")
    print(f"📋 Repository: {test_repo}")
    print()

    try:
        async with GitHubWorkflowFixer(test_repo, token) as fixer:
            # Test 1: Get workflow runs
            print("📊 Test 1: Fetching workflow runs...")
            runs = await fixer.get_workflow_runs(limit=5)
            print(f"✅ Retrieved {len(runs)} workflow runs")

            if runs:
                print("📋 Recent runs:")
                for run in runs[:3]:
                    status = "✅" if run.conclusion == "success" else "❌" if run.is_failed else "⏳"
                    print(f"   {status} {run.name} ({run.head_branch}) - {run.conclusion or run.status}")

            # Test 2: Analyze failures (if any exist)
            print("\n🔍 Test 2: Analyzing workflow failures...")
            analysis = await fixer.analyze_workflow_failures(runs)

            if analysis.failed_runs:
                print(f"❌ Found {len(analysis.failed_runs)} failed runs")
                print("📋 Common issues:")
                for issue in analysis.common_issues:
                    print(f"   • {issue}")
            else:
                print("✅ No failed workflows found")

            # Test 3: Get workflow status
            print("\n📈 Test 3: Getting workflow status summary...")
            # This is a simplified version of the MCP tool
            total = len(runs)
            failed = len([r for r in runs if r.is_failed])
            success = len([r for r in runs if r.status == "completed" and r.conclusion == "success"])
            pending = len([r for r in runs if r.status != "completed"])

            print(f"📊 Status Summary:")
            print(f"   Total: {total}")
            print(f"   Successful: {success}")
            print(f"   Failed: {failed}")
            print(f"   Pending: {pending}")

            print("\n🎉 All tests completed successfully!")
            return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
