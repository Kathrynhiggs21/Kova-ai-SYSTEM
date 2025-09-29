#!/bin/bash

# Script to create the ready-to-merge label for Mergify
# Usage: ./create_mergify_label.sh

echo "🏷️  Creating ready-to-merge label for Mergify..."

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed."
    echo "📱 Please create the label manually:"
    echo "   1. Go to https://github.com/Kathrynhiggs21/Kova-ai-SYSTEM/labels"
    echo "   2. Click 'New label'"
    echo "   3. Name: ready-to-merge"
    echo "   4. Description: Ready for automatic merge by Mergify"
    echo "   5. Color: #0e8a16 (green)"
    exit 1
fi

# Create the label
gh label create "ready-to-merge" \
    --description "Ready for automatic merge by Mergify" \
    --color "0e8a16" \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Label 'ready-to-merge' created successfully!"
else
    echo "ℹ️  Label 'ready-to-merge' may already exist or there was an issue creating it."
    echo "📋 You can check existing labels with: gh label list"
fi

echo ""
echo "🎉 Setup complete! You can now use the 'ready-to-merge' label on pull requests."
echo "📚 See MERGIFY_SETUP.md for complete instructions."