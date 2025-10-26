#!/bin/bash
#
# Log OpenSSL Package Upload Completion
#
# This script provides a convenient wrapper for logging package upload completion.
# Usage: ./log-upload-completion.sh [remote_name]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Set environment variables for the Python script
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Run the Python logging script
python3 "$SCRIPT_DIR/log-upload-completion.py" "$@"

echo ""
echo "📋 Upload completion logged successfully!"
echo "💡 Use this script in your CI/CD pipelines after 'conan upload' commands"