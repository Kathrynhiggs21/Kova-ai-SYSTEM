#!/usr/bin/env python3
"""
Kova File Organizer

This script organizes files into the Kova Master Hub structure based on
the analysis from gdrive_import.py or local file scanning.
"""

import os
import json
import shutil
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


# Folder structure mapping
FOLDER_STRUCTURE = {
    'CORE': '01-Core-System',
    'REPO': '02-Repositories',
    'INT': '03-Integrations',
    'DATA': '04-Data-Management',
    'DEV': '05-Development',
    'OPS': '06-Operations',
    'COM': '07-Communication',
    'RES': '08-Resources',
    'PURGATORY': '09-Purgatory',
    'META': '10-Meta',
    'UNKNOWN': '09-Purgatory/To-Review/Needs-Categorization'
}

# Subcategory mapping
SUBCATEGORIES = {
    'CORE': {
        'documentation': 'Documentation',
        'config': 'Configuration',
        'deployment': 'Deployment'
    },
    'INT': {
        'google': 'Google-Drive',
        'claude': 'Claude-AI',
        'github': 'GitHub',
        'appsheet': 'AppSheet'
    },
    'DATA': {
        'active': 'Active-Data',
        'archive': 'Archives',
        'backup': 'Backups'
    },
    'DEV': {
        'active': 'Active-Projects',
        'prototype': 'Prototypes',
        'experiment': 'Experiments'
    },
    'OPS': {
        'monitor': 'Monitoring',
        'maintenance': 'Maintenance',
        'security': 'Security'
    }
}


class FileOrganizer:
    """Organize files into Kova Master Hub structure"""

    def __init__(self, base_path: str, dry_run: bool = True):
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.stats = {
            'processed': 0,
            'moved': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }

    def log(self, message: str, color: str = Colors.RESET):
        """Print colored message"""
        print(f"{color}{message}{Colors.RESET}")

    def create_folder_structure(self):
        """Create the Kova Master Hub folder structure"""
        self.log("\n📁 Creating Kova Master Hub folder structure...", Colors.BOLD)

        folders_to_create = [
            '01-Core-System/Documentation/Architecture',
            '01-Core-System/Documentation/API-Reference',
            '01-Core-System/Documentation/Setup-Guides',
            '01-Core-System/Documentation/User-Manuals',
            '01-Core-System/Configuration/Production',
            '01-Core-System/Configuration/Development',
            '01-Core-System/Configuration/Testing',
            '01-Core-System/Deployment/Docker',
            '01-Core-System/Deployment/Kubernetes',
            '01-Core-System/Deployment/CI-CD',

            '02-Repositories/Kova-ai-SYSTEM',
            '02-Repositories/kova-ai',
            '02-Repositories/kova-ai-site',
            '02-Repositories/kova-ai-mem0',
            '02-Repositories/kova-ai-docengine',
            '02-Repositories/Kova-AI-Scribbles',

            '03-Integrations/Google-Drive/Setup',
            '03-Integrations/Google-Drive/Scripts',
            '03-Integrations/Google-Drive/Credentials',
            '03-Integrations/Claude-AI/API-Keys',
            '03-Integrations/Claude-AI/Prompts',
            '03-Integrations/Claude-AI/Templates',
            '03-Integrations/GitHub/Webhooks',
            '03-Integrations/GitHub/Actions',
            '03-Integrations/GitHub/Tokens',
            '03-Integrations/AppSheet/Apps',
            '03-Integrations/AppSheet/Data-Sources',
            '03-Integrations/AppSheet/Workflows',

            '04-Data-Management/Active-Data/Databases',
            '04-Data-Management/Active-Data/File-Storage',
            '04-Data-Management/Archives/2024',
            '04-Data-Management/Archives/2023',
            '04-Data-Management/Backups/Daily',
            '04-Data-Management/Backups/Weekly',
            '04-Data-Management/Backups/Monthly',

            '05-Development/Active-Projects',
            '05-Development/Prototypes',
            '05-Development/Experiments',
            '05-Development/Code-Snippets',
            '05-Development/Templates',

            '06-Operations/Monitoring/Logs',
            '06-Operations/Monitoring/Metrics',
            '06-Operations/Monitoring/Alerts',
            '06-Operations/Maintenance/Schedules',
            '06-Operations/Maintenance/Procedures',
            '06-Operations/Security/Credentials',
            '06-Operations/Security/Access-Control',

            '07-Communication/Email/Threads',
            '07-Communication/Email/Attachments',
            '07-Communication/Meetings/Notes',
            '07-Communication/Meetings/Recordings',
            '07-Communication/Collaboration/Shared-Docs',

            '08-Resources/Learning/Tutorials',
            '08-Resources/Learning/References',
            '08-Resources/Assets/Images',
            '08-Resources/Assets/Icons',
            '08-Resources/External-Docs',

            '09-Purgatory/To-Review/Duplicates',
            '09-Purgatory/To-Review/Unclear',
            '09-Purgatory/To-Review/Needs-Categorization',
            '09-Purgatory/Deprecated/Old-Versions',
            '09-Purgatory/Deprecated/Replaced',
            '09-Purgatory/For-Deletion/Verified-Duplicates',
            '09-Purgatory/For-Deletion/Junk',

            '10-Meta/Organization/File-Index',
            '10-Meta/Scripts/Import',
            '10-Meta/Scripts/Organize',
            '10-Meta/Documentation/How-To',
        ]

        created = 0
        for folder in folders_to_create:
            full_path = self.base_path / folder
            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
                created += 1
            else:
                self.log(f"  Would create: {folder}", Colors.CYAN)

        if not self.dry_run:
            self.log(f"✅ Created {created} folders", Colors.GREEN)
        else:
            self.log(f"  (Dry run: would create {len(folders_to_create)} folders)", Colors.YELLOW)

    def generate_new_filename(self, file_info: Dict[str, Any]) -> str:
        """Generate standardized filename"""
        # Get date
        if 'modified' in file_info:
            date = file_info['modified'][:10]  # YYYY-MM-DD
        else:
            date = datetime.now().strftime('%Y-%m-%d')

        # Get category
        category = file_info.get('category', 'UNKNOWN')

        # Get project (from keywords or name)
        name = file_info.get('name', 'file')
        project = 'Kova-AI'  # Default
        if 'mem0' in name.lower():
            project = 'Kova-Mem0'
        elif 'site' in name.lower():
            project = 'Kova-Site'
        elif 'docengine' in name.lower():
            project = 'Kova-DocEngine'
        elif 'multi-repo' in name.lower() or 'multirepo' in name.lower():
            project = 'Multi-Repo'

        # Get description (clean filename)
        desc = Path(name).stem
        desc = re.sub(r'[^a-zA-Z0-9-]', '-', desc)
        desc = re.sub(r'-+', '-', desc)
        desc = desc.strip('-')[:50]  # Max 50 chars

        # Get extension
        ext = Path(name).suffix

        # Get version
        version = 'v1.0'
        if 'draft' in name.lower():
            version = 'draft'
        elif 'final' in name.lower():
            version = 'final'
        else:
            # Try to extract version
            version_match = re.search(r'v?(\d+)\.(\d+)', name)
            if version_match:
                version = f"v{version_match.group(1)}.{version_match.group(2)}"

        # Construct filename
        new_name = f"{date}_{category}_{project}_{desc}_{version}{ext}"

        return new_name

    def determine_destination(self, file_info: Dict[str, Any]) -> Path:
        """Determine destination folder for file"""
        category = file_info.get('category', 'UNKNOWN')
        name = file_info.get('name', '').lower()

        # Get base category folder
        base_folder = FOLDER_STRUCTURE.get(category, FOLDER_STRUCTURE['UNKNOWN'])

        # Determine subcategory
        subcategory = None
        if category == 'CORE':
            if 'architecture' in name or 'diagram' in name:
                subcategory = 'Documentation/Architecture'
            elif 'api' in name or 'endpoint' in name:
                subcategory = 'Documentation/API-Reference'
            elif 'setup' in name or 'guide' in name:
                subcategory = 'Documentation/Setup-Guides'
            elif 'config' in name or 'env' in name:
                subcategory = 'Configuration/Production'
            elif 'docker' in name:
                subcategory = 'Deployment/Docker'

        elif category == 'INT':
            if 'google' in name or 'drive' in name:
                subcategory = 'Google-Drive/Scripts'
            elif 'claude' in name or 'anthropic' in name:
                subcategory = 'Claude-AI/Prompts'
            elif 'github' in name or 'webhook' in name:
                subcategory = 'GitHub/Webhooks'
            elif 'appsheet' in name:
                subcategory = 'AppSheet/Apps'

        elif category == 'DATA':
            if 'backup' in name:
                subcategory = 'Backups/Daily'
            elif 'archive' in name:
                subcategory = 'Archives/2024'
            else:
                subcategory = 'Active-Data/Databases'

        elif category == 'DEV':
            if 'prototype' in name or 'proto' in name:
                subcategory = 'Prototypes'
            elif 'experiment' in name or 'test' in name:
                subcategory = 'Experiments'
            else:
                subcategory = 'Active-Projects'

        # Build full path
        if subcategory:
            destination = self.base_path / base_folder / subcategory
        else:
            destination = self.base_path / base_folder

        return destination

    def organize_file(self, file_info: Dict[str, Any], source_path: Optional[Path] = None):
        """Organize a single file"""
        self.stats['processed'] += 1

        # Determine destination
        destination_folder = self.determine_destination(file_info)

        # Generate new filename
        new_filename = self.generate_new_filename(file_info)

        # Full destination path
        destination_path = destination_folder / new_filename

        # Log action
        if source_path:
            action = f"Move: {source_path.name} -> {destination_path.relative_to(self.base_path)}"
        else:
            action = f"Would download: {file_info.get('name')} -> {destination_path.relative_to(self.base_path)}"

        # Check relevance score
        relevance = file_info.get('relevance_score', 5)
        if relevance < 5:
            self.log(f"  ⚠️  Low relevance ({relevance}): {action}", Colors.YELLOW)
            # Send to purgatory
            destination_path = self.base_path / '09-Purgatory/To-Review/Needs-Categorization' / new_filename

        # Perform action
        if not self.dry_run and source_path:
            try:
                destination_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(destination_path))
                self.stats['moved'] += 1
                self.log(f"  ✅ {action}", Colors.GREEN)
            except Exception as e:
                self.stats['errors'] += 1
                self.log(f"  ❌ Error: {e}", Colors.RED)
        else:
            self.log(f"  📝 {action}", Colors.CYAN)

    def organize_from_inventory(self, inventory_file: Path):
        """Organize files based on inventory JSON"""
        self.log(f"\n📋 Loading inventory from: {inventory_file}", Colors.BOLD)

        with open(inventory_file, 'r') as f:
            inventory = json.load(f)

        self.log(f"  Found {len(inventory)} files to organize", Colors.CYAN)

        # Sort by relevance score (highest first)
        inventory.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)

        # Organize each file
        for i, file_info in enumerate(inventory):
            if i % 50 == 0 and i > 0:
                self.log(f"\n  Progress: {i}/{len(inventory)}", Colors.MAGENTA)

            self.organize_file(file_info)

    def print_summary(self):
        """Print organization summary"""
        self.log("\n" + "="*80, Colors.BOLD)
        self.log("📊 ORGANIZATION SUMMARY", Colors.BOLD)
        self.log("="*80, Colors.BOLD)

        self.log(f"\n  Processed: {self.stats['processed']}", Colors.CYAN)
        self.log(f"  Moved: {self.stats['moved']}", Colors.GREEN)
        self.log(f"  Renamed: {self.stats['renamed']}", Colors.YELLOW)
        self.log(f"  Skipped: {self.stats['skipped']}", Colors.YELLOW)
        self.log(f"  Errors: {self.stats['errors']}", Colors.RED)

        if self.dry_run:
            self.log(f"\n⚠️  DRY RUN MODE - No files were actually moved", Colors.YELLOW)
            self.log(f"  Run without --dry-run to execute changes", Colors.YELLOW)
        else:
            self.log(f"\n✅ Organization complete!", Colors.GREEN)

    def run(self, inventory_file: Optional[Path] = None):
        """Main execution"""
        self.log("\n" + "="*80, Colors.BOLD)
        self.log("📁 KOVA FILE ORGANIZER", Colors.BOLD)
        self.log("="*80 + "\n", Colors.BOLD)

        if self.dry_run:
            self.log("⚠️  Running in DRY RUN mode - no files will be moved\n", Colors.YELLOW)

        # Create folder structure
        self.create_folder_structure()

        # Organize files
        if inventory_file and inventory_file.exists():
            self.organize_from_inventory(inventory_file)
        else:
            self.log("\n⚠️  No inventory file provided or file not found", Colors.YELLOW)
            self.log("  Use gdrive_import.py to generate an inventory first", Colors.YELLOW)

        # Print summary
        self.print_summary()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Organize Kova files into master hub structure')
    parser.add_argument('base_path', help='Base path for Kova Master Hub')
    parser.add_argument('--inventory', help='Path to inventory JSON file from gdrive_import.py')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (no actual changes)')
    parser.add_argument('--execute', action='store_true', help='Execute mode (actually move files)')

    args = parser.parse_args()

    # Default to dry run unless --execute is specified
    dry_run = not args.execute

    organizer = FileOrganizer(args.base_path, dry_run=dry_run)

    inventory_path = Path(args.inventory) if args.inventory else None
    organizer.run(inventory_file=inventory_path)


if __name__ == '__main__':
    main()
