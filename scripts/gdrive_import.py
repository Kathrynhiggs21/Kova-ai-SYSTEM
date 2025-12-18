#!/usr/bin/env python3
"""
Google Drive Import Tool for Kova AI System

This script scans Google Drive for Kova-related files, analyzes them,
and prepares them for organization into the Kova Master Hub structure.
"""

import os
import json
import hashlib
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    import pickle
    GDRIVE_AVAILABLE = True
except ImportError:
    GDRIVE_AVAILABLE = False
    print("⚠️  Google Drive API not installed. Install with:")
    print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# Configuration
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
KOVA_KEYWORDS = [
    'kova', 'kova-ai', 'kova ai', 'kovaai',
    'purgatory', 'claude', 'multi-repo',
    'appsheet', 'webhook'
]

# File categories
CATEGORIES = {
    'CORE': ['architecture', 'api', 'setup', 'deployment', 'config'],
    'REPO': ['repository', 'github', 'git', 'commit', 'branch'],
    'INT': ['integration', 'api-key', 'oauth', 'webhook', 'credential'],
    'DATA': ['database', 'backup', 'export', 'csv', 'json', 'sql'],
    'DEV': ['dev', 'development', 'prototype', 'experiment', 'test'],
    'OPS': ['ops', 'operations', 'monitor', 'log', 'alert', 'security'],
    'COM': ['email', 'meeting', 'notes', 'discussion', 'thread'],
    'RES': ['tutorial', 'guide', 'reference', 'asset', 'template']
}


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


class GoogleDriveImporter:
    """Import and analyze Kova files from Google Drive"""

    def __init__(self, credentials_path: str = 'credentials.json'):
        self.credentials_path = credentials_path
        self.service = None
        self.file_inventory = []
        self.duplicates = []
        self.categories = {}

    def log(self, message: str, color: str = Colors.RESET):
        """Print colored message"""
        print(f"{color}{message}{Colors.RESET}")

    def authenticate(self) -> bool:
        """Authenticate with Google Drive API"""
        if not GDRIVE_AVAILABLE:
            self.log("❌ Google Drive API not available", Colors.RED)
            return False

        creds = None
        token_path = 'token.pickle'

        # Load existing credentials
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    self.log(f"❌ Credentials file not found: {self.credentials_path}", Colors.RED)
                    self.log("   Get credentials from: https://console.cloud.google.com/", Colors.YELLOW)
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('drive', 'v3', credentials=creds)
        self.log("✅ Authenticated with Google Drive", Colors.GREEN)
        return True

    def search_kova_files(self) -> List[Dict[str, Any]]:
        """Search for all Kova-related files"""
        self.log("\n🔍 Searching for Kova-related files...", Colors.BOLD)

        if not self.service:
            self.log("❌ Not authenticated", Colors.RED)
            return []

        all_files = []
        page_token = None

        try:
            while True:
                # Search for files
                query = ' or '.join([f"name contains '{kw}'" for kw in KOVA_KEYWORDS])
                results = self.service.files().list(
                    q=query,
                    pageSize=100,
                    pageToken=page_token,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, createdTime, owners, parents, webViewLink)"
                ).execute()

                files = results.get('files', [])
                all_files.extend(files)

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

                self.log(f"  Found {len(all_files)} files so far...", Colors.CYAN)

            self.log(f"✅ Found {len(all_files)} Kova-related files", Colors.GREEN)
            return all_files

        except Exception as e:
            self.log(f"❌ Error searching files: {e}", Colors.RED)
            return []

    def analyze_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single file"""
        name = file_info['name'].lower()

        # Calculate relevance score
        relevance_score = 0

        # Keyword matching (0-4 points)
        keyword_matches = sum(1 for kw in KOVA_KEYWORDS if kw in name)
        relevance_score += min(keyword_matches * 2, 4)

        # Recency (0-3 points)
        if 'modifiedTime' in file_info:
            modified = datetime.fromisoformat(file_info['modifiedTime'].replace('Z', '+00:00'))
            days_old = (datetime.now(modified.tzinfo) - modified).days
            if days_old < 30:
                relevance_score += 3
            elif days_old < 90:
                relevance_score += 2
            elif days_old < 180:
                relevance_score += 1

        # File type (0-2 points)
        mime_type = file_info.get('mimeType', '')
        if 'document' in mime_type or 'text' in mime_type:
            relevance_score += 2
        elif 'spreadsheet' in mime_type or 'json' in mime_type:
            relevance_score += 2
        elif 'folder' in mime_type:
            relevance_score += 1

        # Size (0-1 point)
        size = int(file_info.get('size', 0))
        if 1024 < size < 10*1024*1024:  # Between 1KB and 10MB
            relevance_score += 1

        # Categorize
        category = self.categorize_file(name)

        return {
            'id': file_info['id'],
            'name': file_info['name'],
            'mime_type': mime_type,
            'size': size,
            'modified': file_info.get('modifiedTime'),
            'created': file_info.get('createdTime'),
            'owners': file_info.get('owners', []),
            'parents': file_info.get('parents', []),
            'web_link': file_info.get('webViewLink'),
            'relevance_score': min(relevance_score, 10),
            'category': category,
            'keywords_found': [kw for kw in KOVA_KEYWORDS if kw in name]
        }

    def categorize_file(self, filename: str) -> str:
        """Categorize file based on name and content"""
        filename_lower = filename.lower()

        # Check each category
        for category, keywords in CATEGORIES.items():
            if any(kw in filename_lower for kw in keywords):
                return category

        return 'UNKNOWN'

    def find_duplicates(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find duplicate files"""
        self.log("\n🔍 Detecting duplicates...", Colors.BOLD)

        # Group by name
        by_name = {}
        for f in files:
            name = f['name'].lower()
            if name not in by_name:
                by_name[name] = []
            by_name[name].append(f)

        # Find exact name duplicates
        exact_duplicates = []
        for name, file_list in by_name.items():
            if len(file_list) > 1:
                exact_duplicates.append({
                    'type': 'exact_name',
                    'name': name,
                    'count': len(file_list),
                    'files': file_list
                })

        # Find similar names
        similar_duplicates = []
        names = list(by_name.keys())
        for i, name1 in enumerate(names):
            for name2 in names[i+1:]:
                similarity = self.calculate_similarity(name1, name2)
                if similarity > 0.8:  # 80% similar
                    similar_duplicates.append({
                        'type': 'similar_name',
                        'similarity': similarity,
                        'name1': name1,
                        'name2': name2,
                        'files': by_name[name1] + by_name[name2]
                    })

        self.log(f"  Found {len(exact_duplicates)} exact name duplicates", Colors.YELLOW)
        self.log(f"  Found {len(similar_duplicates)} similar name duplicates", Colors.YELLOW)

        return exact_duplicates + similar_duplicates

    def calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple Levenshtein-like approach
        if s1 == s2:
            return 1.0

        # Convert to sets of words
        words1 = set(re.findall(r'\w+', s1.lower()))
        words2 = set(re.findall(r'\w+', s2.lower()))

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def generate_report(self, analyzed_files: List[Dict[str, Any]], duplicates: List[Dict[str, Any]]):
        """Generate analysis report"""
        self.log("\n" + "="*80, Colors.BOLD)
        self.log("📊 KOVA FILE ANALYSIS REPORT", Colors.BOLD)
        self.log("="*80, Colors.BOLD)

        # Summary
        total_files = len(analyzed_files)
        total_size = sum(f['size'] for f in analyzed_files)

        self.log(f"\n📁 Total Files: {total_files}", Colors.CYAN)
        self.log(f"💾 Total Size: {self.format_size(total_size)}", Colors.CYAN)

        # By category
        self.log(f"\n📂 Files by Category:", Colors.BOLD)
        category_counts = {}
        for f in analyzed_files:
            cat = f['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1

        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total_files) * 100
            self.log(f"  {cat:10s}: {count:4d} files ({pct:5.1f}%)", Colors.YELLOW)

        # By relevance
        self.log(f"\n⭐ Files by Relevance Score:", Colors.BOLD)
        relevance_counts = {
            'Critical (9-10)': 0,
            'Important (7-8)': 0,
            'Useful (5-6)': 0,
            'Questionable (3-4)': 0,
            'Irrelevant (1-2)': 0
        }

        for f in analyzed_files:
            score = f['relevance_score']
            if score >= 9:
                relevance_counts['Critical (9-10)'] += 1
            elif score >= 7:
                relevance_counts['Important (7-8)'] += 1
            elif score >= 5:
                relevance_counts['Useful (5-6)'] += 1
            elif score >= 3:
                relevance_counts['Questionable (3-4)'] += 1
            else:
                relevance_counts['Irrelevant (1-2)'] += 1

        for level, count in relevance_counts.items():
            pct = (count / total_files) * 100
            self.log(f"  {level:20s}: {count:4d} files ({pct:5.1f}%)", Colors.GREEN)

        # Duplicates
        self.log(f"\n🔁 Duplicates Found: {len(duplicates)}", Colors.BOLD)
        if duplicates:
            for dup in duplicates[:10]:  # Show first 10
                if dup['type'] == 'exact_name':
                    self.log(f"  Exact: '{dup['name']}' ({dup['count']} copies)", Colors.YELLOW)
                else:
                    self.log(f"  Similar: {dup['similarity']:.0%} - '{dup['name1']}' & '{dup['name2']}'", Colors.YELLOW)

            if len(duplicates) > 10:
                self.log(f"  ... and {len(duplicates) - 10} more", Colors.YELLOW)

        # Recommendations
        self.log(f"\n💡 Recommendations:", Colors.BOLD)

        low_relevance = sum(1 for f in analyzed_files if f['relevance_score'] < 5)
        if low_relevance > 0:
            self.log(f"  • Review {low_relevance} low-relevance files for deletion", Colors.CYAN)

        if duplicates:
            self.log(f"  • Resolve {len(duplicates)} duplicate file groups", Colors.CYAN)

        unknown_cat = category_counts.get('UNKNOWN', 0)
        if unknown_cat > 0:
            self.log(f"  • Categorize {unknown_cat} unknown files", Colors.CYAN)

        self.log(f"  • Move questionable files to Purgatory folder", Colors.CYAN)
        self.log(f"  • Archive files older than 6 months", Colors.CYAN)

    def format_size(self, size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def save_inventory(self, analyzed_files: List[Dict[str, Any]], duplicates: List[Dict[str, Any]]):
        """Save inventory to JSON"""
        output_dir = Path(__file__).parent.parent / 'kova_file_inventory'
        output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save analyzed files
        inventory_file = output_dir / f'inventory_{timestamp}.json'
        with open(inventory_file, 'w') as f:
            json.dump(analyzed_files, f, indent=2)

        # Save duplicates
        duplicates_file = output_dir / f'duplicates_{timestamp}.json'
        with open(duplicates_file, 'w') as f:
            json.dump(duplicates, f, indent=2)

        # Save summary
        summary_file = output_dir / f'summary_{timestamp}.txt'
        with open(summary_file, 'w') as f:
            f.write(f"Kova File Analysis Summary\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"\nTotal Files: {len(analyzed_files)}\n")
            f.write(f"Total Duplicates: {len(duplicates)}\n")
            f.write(f"\nFiles by Category:\n")
            category_counts = {}
            for file in analyzed_files:
                cat = file['category']
                category_counts[cat] = category_counts.get(cat, 0) + 1
            for cat, count in sorted(category_counts.items()):
                f.write(f"  {cat}: {count}\n")

        self.log(f"\n💾 Inventory saved:", Colors.BOLD)
        self.log(f"  Files: {inventory_file}", Colors.GREEN)
        self.log(f"  Duplicates: {duplicates_file}", Colors.GREEN)
        self.log(f"  Summary: {summary_file}", Colors.GREEN)

    def run(self):
        """Main execution"""
        self.log("\n" + "="*80, Colors.BOLD)
        self.log("🚀 KOVA GOOGLE DRIVE IMPORT TOOL", Colors.BOLD)
        self.log("="*80 + "\n", Colors.BOLD)

        # Authenticate
        if not self.authenticate():
            self.log("\n❌ Authentication failed. Exiting.", Colors.RED)
            return

        # Search files
        files = self.search_kova_files()
        if not files:
            self.log("\n⚠️  No files found", Colors.YELLOW)
            return

        # Analyze files
        self.log(f"\n🔍 Analyzing {len(files)} files...", Colors.BOLD)
        analyzed_files = []
        for i, file_info in enumerate(files):
            if i % 10 == 0:
                self.log(f"  Progress: {i}/{len(files)}", Colors.CYAN)
            analyzed_files.append(self.analyze_file(file_info))

        # Find duplicates
        duplicates = self.find_duplicates(analyzed_files)

        # Generate report
        self.generate_report(analyzed_files, duplicates)

        # Save inventory
        self.save_inventory(analyzed_files, duplicates)

        self.log("\n✅ Analysis complete!", Colors.GREEN)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Import and analyze Kova files from Google Drive')
    parser.add_argument('--credentials', default='credentials.json', help='Path to Google credentials file')
    args = parser.parse_args()

    importer = GoogleDriveImporter(credentials_path=args.credentials)
    importer.run()


if __name__ == '__main__':
    main()
