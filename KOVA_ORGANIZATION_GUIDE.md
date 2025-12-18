# Kova Master Hub Organization Guide

## Complete Guide to Organizing All Kova Files from Google Drive

This guide walks you through the complete process of importing, analyzing, organizing, and maintaining all Kova-related files from Google Drive and other sources.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Discovery & Analysis](#phase-1-discovery--analysis)
4. [Phase 2: Purgatory Review](#phase-2-purgatory-review)
5. [Phase 3: Organization](#phase-3-organization)
6. [Phase 4: Maintenance](#phase-4-maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

For those who want to get started immediately:

```bash
# 1. Set up Google Drive API credentials
# Download from: https://console.cloud.google.com/
# Place as: credentials.json

# 2. Install dependencies
pip install google-auth google-auth-oauthlib google-api-python-client

# 3. Run discovery and analysis
python3 scripts/gdrive_import.py

# 4. Review the generated inventory
cat kova_file_inventory/summary_*.txt

# 5. Create folder structure (dry run first)
python3 scripts/file_organizer.py ~/Kova-Master-Hub --dry-run

# 6. Execute organization
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory kova_file_inventory/inventory_*.json \
  --execute
```

---

## Prerequisites

### Required Software

- **Python 3.9+**
- **Google Drive API** access
- **jq** (for JSON processing, optional but recommended)

### Required API Credentials

#### Google Drive API Setup

1. **Go to Google Cloud Console**
   ```
   https://console.cloud.google.com/
   ```

2. **Create a new project** (or use existing)
   - Click "Select a Project" → "New Project"
   - Name it "Kova File Management"

3. **Enable Google Drive API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click "Enable"

4. **Create credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Name: "Kova Organizer"
   - Download the JSON file
   - Save as `credentials.json` in the Kova-ai-SYSTEM directory

5. **Install Python libraries**
   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client
   ```

---

## Phase 1: Discovery & Analysis

### Step 1: Run Google Drive Import

```bash
cd Kova-ai-SYSTEM

# Run the import tool
python3 scripts/gdrive_import.py
```

**What happens:**
- Opens browser for Google authentication (first time only)
- Scans Google Drive for Kova-related files
- Analyzes each file for:
  - Relevance score (1-10)
  - Category (CORE, INT, DATA, DEV, etc.)
  - Duplicates (exact and similar)
  - Keywords found
- Generates comprehensive report

**Output files:**
```
kova_file_inventory/
├── inventory_TIMESTAMP.json      # All files with metadata
├── duplicates_TIMESTAMP.json     # Duplicate groups
└── summary_TIMESTAMP.txt         # Human-readable summary
```

### Step 2: Review the Analysis Report

```bash
# View the summary
cat kova_file_inventory/summary_*.txt

# Or view the full report (if you ran the tool in terminal)
# It shows:
# - Total files found
# - Files by category
# - Files by relevance score
# - Duplicates detected
# - Recommendations
```

**Example output:**
```
📊 KOVA FILE ANALYSIS REPORT

📁 Total Files: 342
💾 Total Size: 1.2 GB

📂 Files by Category:
  CORE      :   45 files (13.2%)
  INT       :   78 files (22.8%)
  DATA      :   23 files (6.7%)
  DEV       :   89 files (26.0%)
  COM       :   67 files (19.6%)
  UNKNOWN   :   40 files (11.7%)

⭐ Files by Relevance Score:
  Critical (9-10)      :   23 files (6.7%)
  Important (7-8)      :   87 files (25.4%)
  Useful (5-6)         :  145 files (42.4%)
  Questionable (3-4)   :   67 files (19.6%)
  Irrelevant (1-2)     :   20 files (5.8%)

🔁 Duplicates Found: 15
```

### Step 3: Analyze the Inventory

```bash
# View files with low relevance (candidates for purgatory)
cat kova_file_inventory/inventory_*.json | \
  jq '.[] | select(.relevance_score < 5) | {name, score: .relevance_score}'

# View files by category
cat kova_file_inventory/inventory_*.json | \
  jq 'group_by(.category) | map({category: .[0].category, count: length})'

# View exact duplicates
cat kova_file_inventory/duplicates_*.json | \
  jq '.[] | select(.type == "exact_name")'
```

---

## Phase 2: Purgatory Review

### Understanding Purgatory

Files go to purgatory if they have:
- **Low relevance** (score < 5)
- **Unclear purpose**
- **Duplicate status**
- **Unknown category**

### Step 1: Review Questionable Files

```bash
# List all low-relevance files
python3 << 'EOF'
import json
from pathlib import Path

# Find the latest inventory
inventory_dir = Path('kova_file_inventory')
inventory_file = sorted(inventory_dir.glob('inventory_*.json'))[-1]

with open(inventory_file) as f:
    files = json.load(f)

print("\n🔍 LOW RELEVANCE FILES (Score < 5)\n")
low_relevance = [f for f in files if f.get('relevance_score', 0) < 5]

for f in sorted(low_relevance, key=lambda x: x['relevance_score']):
    print(f"  Score {f['relevance_score']}: {f['name']}")
    print(f"    Category: {f['category']}")
    print(f"    Keywords: {', '.join(f.get('keywords_found', []))}")
    print(f"    Link: {f.get('web_link', 'N/A')}\n")
EOF
```

### Step 2: Review Duplicates

```bash
# List all duplicates
python3 << 'EOF'
import json
from pathlib import Path

duplicates_dir = Path('kova_file_inventory')
duplicates_file = sorted(duplicates_dir.glob('duplicates_*.json'))[-1]

with open(duplicates_file) as f:
    duplicates = json.load(f)

print("\n🔁 DUPLICATE FILES\n")
for dup in duplicates:
    if dup['type'] == 'exact_name':
        print(f"  Exact duplicate: {dup['name']}")
        print(f"    Count: {dup['count']} copies")
        for file in dup['files']:
            print(f"      - Modified: {file.get('modified', 'N/A')}")
            print(f"        Link: {file.get('web_link', 'N/A')}")
    print()
EOF
```

### Step 3: Make Decisions

Create a decisions file:

```bash
cat > purgatory_decisions.json << 'EOF'
{
  "delete": [
    "file_id_1",
    "file_id_2"
  ],
  "keep_newest": [
    {
      "name": "duplicate_file.pdf",
      "keep_id": "file_id_3",
      "delete_ids": ["file_id_4", "file_id_5"]
    }
  ],
  "recategorize": [
    {
      "file_id": "file_id_6",
      "new_category": "DATA",
      "reason": "Actually a database export"
    }
  ],
  "archive": [
    "file_id_7",
    "file_id_8"
  ]
}
EOF
```

---

## Phase 3: Organization

### Step 1: Create Folder Structure (Dry Run)

```bash
# Create the Kova Master Hub folder structure (dry run first)
python3 scripts/file_organizer.py ~/Kova-Master-Hub --dry-run

# This shows what folders would be created without actually creating them
```

**Output:**
```
📁 Creating Kova Master Hub folder structure...
  Would create: 01-Core-System/Documentation/Architecture
  Would create: 01-Core-System/Documentation/API-Reference
  Would create: 01-Core-System/Configuration/Production
  ...
  (Dry run: would create 75 folders)
```

### Step 2: Organize Files with Inventory (Dry Run)

```bash
# Find the latest inventory file
INVENTORY=$(ls -t kova_file_inventory/inventory_*.json | head -1)

# Dry run organization
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory "$INVENTORY" \
  --dry-run
```

**Output:**
```
📁 KOVA FILE ORGANIZER

⚠️  Running in DRY RUN mode - no files will be moved

📋 Loading inventory from: kova_file_inventory/inventory_20241106_143022.json
  Found 342 files to organize

  📝 Would download: Architecture-Diagram.pdf -> 01-Core-System/Documentation/Architecture/2024-11-06_CORE_Kova-AI_Architecture-Diagram_v1.0.pdf
  📝 Would download: API-Reference.md -> 01-Core-System/Documentation/API-Reference/2024-11-06_CORE_Kova-AI_API-Reference_v2.1.md
  ⚠️  Low relevance (3): old-notes.txt -> 09-Purgatory/To-Review/Needs-Categorization/2024-11-06_UNKNOWN_Kova-AI_old-notes_v1.0.txt
  ...

📊 ORGANIZATION SUMMARY

  Processed: 342
  Moved: 0
  Renamed: 0
  Skipped: 0
  Errors: 0

⚠️  DRY RUN MODE - No files were actually moved
  Run without --dry-run to execute changes
```

### Step 3: Review the Plan

Check the dry run output carefully:
- Are files going to the right categories?
- Are filenames standardized correctly?
- Are low-relevance files going to purgatory?

### Step 4: Execute Organization

```bash
# Execute the organization
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory "$INVENTORY" \
  --execute

# This will actually move/organize files
```

### Step 5: Verify Organization

```bash
# Check the structure
tree -L 2 ~/Kova-Master-Hub

# Count files in each category
find ~/Kova-Master-Hub -type f | \
  awk -F/ '{print $(NF-2)}' | sort | uniq -c

# Check purgatory
ls -la ~/Kova-Master-Hub/09-Purgatory/To-Review/
```

---

## Phase 4: Maintenance

### Daily Maintenance

```bash
#!/bin/bash
# daily_maintenance.sh

# 1. Import new files
python3 scripts/gdrive_import.py

# 2. Organize new files (dry run first)
INVENTORY=$(ls -t kova_file_inventory/inventory_*.json | head -1)
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory "$INVENTORY" \
  --dry-run

# 3. Review and execute if OK
# python3 scripts/file_organizer.py ~/Kova-Master-Hub \
#   --inventory "$INVENTORY" \
#   --execute
```

### Weekly Purgatory Review

```bash
# 1. Check purgatory size
du -sh ~/Kova-Master-Hub/09-Purgatory

# 2. Review files
ls -lhR ~/Kova-Master-Hub/09-Purgatory/To-Review/

# 3. Make decisions:
#    - Delete obvious junk
#    - Recategorize files that belong elsewhere
#    - Archive old but potentially useful files
#    - Move to For-Deletion if confirmed junk
```

### Monthly Archive

```bash
# Archive files older than 6 months
find ~/Kova-Master-Hub -type f -mtime +180 | while read file; do
  # Get year
  year=$(date -r "$file" +%Y)

  # Create archive directory
  mkdir -p ~/Kova-Master-Hub/04-Data-Management/Archives/$year

  # Move file
  mv "$file" ~/Kova-Master-Hub/04-Data-Management/Archives/$year/
done
```

### Quarterly Cleanup

```bash
# 1. Clear verified duplicates
rm -rf ~/Kova-Master-Hub/09-Purgatory/For-Deletion/Verified-Duplicates/*

# 2. Remove junk
rm -rf ~/Kova-Master-Hub/09-Purgatory/For-Deletion/Junk/*

# 3. Archive deprecated files
tar -czf deprecated-$(date +%Y%m%d).tar.gz \
  ~/Kova-Master-Hub/09-Purgatory/Deprecated/

mv deprecated-*.tar.gz ~/Kova-Master-Hub/04-Data-Management/Archives/

# 4. Update file index
python3 scripts/generate_index.py ~/Kova-Master-Hub
```

---

## Advanced Usage

### Filtering by Relevance

```bash
# Only organize files with relevance >= 7
cat "$INVENTORY" | \
  jq '[.[] | select(.relevance_score >= 7)]' > high_relevance.json

python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory high_relevance.json \
  --execute
```

### Category-Specific Organization

```bash
# Only organize CORE files
cat "$INVENTORY" | \
  jq '[.[] | select(.category == "CORE")]' > core_files.json

python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory core_files.json \
  --execute
```

### Custom Naming Convention

Edit `scripts/file_organizer.py` and modify the `generate_new_filename` method to customize the naming convention.

---

## Integration with Repository

### Sync Important Files to Git

```bash
# Create symlinks to important documentation
ln -s ~/Kova-Master-Hub/01-Core-System/Documentation \
  ~/Kova-ai-SYSTEM/docs

# Copy configuration files
cp ~/Kova-Master-Hub/01-Core-System/Configuration/Production/* \
  ~/Kova-ai-SYSTEM/config/

# Add to git
cd ~/Kova-ai-SYSTEM
git add docs config
git commit -m "sync: Update documentation and configuration from Master Hub"
```

---

## Troubleshooting

### Google Drive API Issues

**Problem:** "credentials.json not found"

**Solution:**
```bash
# Download from Google Cloud Console
# Place in Kova-ai-SYSTEM directory
ls -la credentials.json
```

**Problem:** "Token expired"

**Solution:**
```bash
# Remove old token
rm token.pickle

# Re-run script (will re-authenticate)
python3 scripts/gdrive_import.py
```

### Organization Issues

**Problem:** Files not being categorized correctly

**Solution:**
```bash
# Check the category keywords in scripts/gdrive_import.py
# Add more keywords to CATEGORIES dict if needed

# Example: Add "memo" to COM category
CATEGORIES = {
    'COM': ['email', 'meeting', 'notes', 'discussion', 'thread', 'memo'],
    ...
}
```

**Problem:** Too many files in purgatory

**Solution:**
```bash
# Review and recategorize
# Edit the inventory file to fix categories
cat "$INVENTORY" | \
  jq '(.[] | select(.name | contains("specific_file")) | .category) = "CORE"' \
  > updated_inventory.json

# Re-organize with updated inventory
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory updated_inventory.json \
  --execute
```

### Performance Issues

**Problem:** Script is slow with many files

**Solution:**
```bash
# Process files in batches
cat "$INVENTORY" | jq '.[0:100]' > batch1.json
cat "$INVENTORY" | jq '.[100:200]' > batch2.json
# etc...

# Organize each batch
for batch in batch*.json; do
  python3 scripts/file_organizer.py ~/Kova-Master-Hub \
    --inventory "$batch" \
    --execute
  sleep 5
done
```

---

## Best Practices

### 1. Always Dry Run First
```bash
# Never skip the dry run
python3 scripts/file_organizer.py ~/Kova-Master-Hub --dry-run
```

### 2. Review Regularly
- Daily: Check for new files
- Weekly: Review purgatory
- Monthly: Archive old files
- Quarterly: Full cleanup

### 3. Document Decisions
Keep a log of organizational decisions:
```bash
echo "$(date): Moved file X to category Y because Z" >> \
  ~/Kova-Master-Hub/10-Meta/Organization/decisions.log
```

### 4. Backup Before Major Changes
```bash
# Before executing organization
tar -czf backup-$(date +%Y%m%d).tar.gz ~/Kova-Master-Hub
```

### 5. Keep Purgatory Small
- Review weekly
- Make decisions quickly
- Don't let it grow beyond 5% of total files

---

## Quick Reference

### Common Commands

```bash
# Import from Google Drive
python3 scripts/gdrive_import.py

# Organize files (dry run)
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory kova_file_inventory/inventory_*.json \
  --dry-run

# Organize files (execute)
python3 scripts/file_organizer.py ~/Kova-Master-Hub \
  --inventory kova_file_inventory/inventory_*.json \
  --execute

# Check purgatory
find ~/Kova-Master-Hub/09-Purgatory -type f | wc -l

# Archive old files
find ~/Kova-Master-Hub -type f -mtime +180 -exec mv {} \
  ~/Kova-Master-Hub/04-Data-Management/Archives/2024/ \;
```

---

## Support

- **Issues**: See KOVA_FILE_ORGANIZATION.md for structure details
- **Scripts**: Check scripts/gdrive_import.py and scripts/file_organizer.py
- **Questions**: Document in 07-Communication/Collaboration/

---

**Version**: 1.0
**Created**: 2024-11-06
**Last Updated**: 2024-11-06
**Status**: Active
