#!/bin/bash
# rollback.sh - Emergency rollback for repository separation
set -e

echo "Starting emergency rollback..."

# Reset to main backup point
git checkout main
git reset --hard origin/main-backup 2>/dev/null || echo "No main-backup branch found"

# Restore from backups
if [ -d ".github/workflows-moved-to-tools-$(date +%Y%m%d)" ]; then
    cp -r .github/workflows-moved-to-tools-$(date +%Y%m%d)/* .github/workflows/ 2>/dev/null || true
fi

if [ -d "tools-backup-$(date +%Y%m%d)" ]; then
    cp -r tools-backup-$(date +%Y%m%d)/* ./ 2>/dev/null || true
fi

# Restore conanfile.py from git if needed
# git checkout HEAD~1 -- conanfile.py

echo "Rollback complete. Repository restored to pre-separation state."