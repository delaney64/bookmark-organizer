#!/usr/bin/env python3
"""
Chrome Bookmarks Organizer
Processes exported Chrome bookmarks to find duplicates and check connectivity.
"""

import csv
import json
import requests
from bs4 import BeautifulSoup
from collections import defaultdict, Counter
from urllib.parse import urlparse
import time
import sys
from pathlib import Path

class BookmarkOrganizer:
    def __init__(self, bookmarks_file):
        self.bookmarks_file = bookmarks_file
        self.bookmarks = []
        self.duplicates = []
        self.dead_links = []
        self.working_links = []
        
    def parse_bookmarks(self):
        """Parse Chrome bookmarks HTML file"""
        print("Parsing bookmarks file...")
        
        try:
            with open(self.bookmarks_file, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                
            # Find all bookmark links
            links = soup.find_all('a')
            
            for link in links:
                href = link.get('href')
                title = link.get_text(strip=True)
                
                if href and title:
                    self.bookmarks.append({
                        'title': title,
                        'url': href,
                        'domain': urlparse(href).netloc
                    })
                    
            print(f"Found {len(self.bookmarks)} bookmarks")
            
        except Exception as e:
            print(f"Error parsing bookmarks file: {e}")
            sys.exit(1)
    
    def find_duplicates(self):
        """Find duplicate URLs and similar titles"""
        print("Checking for duplicates...")
        
        # Check for duplicate URLs
        url_counts = Counter(bookmark['url'] for bookmark in self.bookmarks)
        duplicate_urls = {url: count for url, count in url_counts.items() if count > 1}
        
        # Check for duplicate titles (case-insensitive)
        title_groups = defaultdict(list)
        for bookmark in self.bookmarks:
            title_lower = bookmark['title'].lower().strip()
            title_groups[title_lower].append(bookmark)
        
        duplicate_titles = {title: bookmarks for title, bookmarks in title_groups.items() 
                          if len(bookmarks) > 1}
        
        # Combine duplicates
        seen_urls = set()
        for bookmark in self.bookmarks:
            url = bookmark['url']
            title_lower = bookmark['title'].lower().strip()
            
            is_duplicate = False
            
            # Check if URL is duplicate
            if url in duplicate_urls and url not in seen_urls:
                duplicate_group = [b for b in self.bookmarks if b['url'] == url]
                self.duplicates.append({
                    'type': 'duplicate_url',
                    'url': url,
                    'count': len(duplicate_group),
                    'titles': [b['title'] for b in duplicate_group]
                })
                seen_urls.add(url)
                is_duplicate = True
            
            # Check if title is duplicate (but different URLs)
            if title_lower in duplicate_titles and not is_duplicate:
                similar_bookmarks = duplicate_titles[title_lower]
                if len(set(b['url'] for b in similar_bookmarks)) > 1:  # Different URLs
                    self.duplicates.append({
                        'type': 'duplicate_title',
                        'title': bookmark['title'],
                        'urls': [b['url'] for b in similar_bookmarks],
                        'count': len(similar_bookmarks)
                    })
        
        print(f"Found {len(self.duplicates)} duplicate groups")
    
    def test_connectivity(self, timeout=10, delay=0.5):
        """Test each bookmark for connectivity"""
        print(f"Testing connectivity for {len(self.bookmarks)} bookmarks...")
        print("This may take a while...")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        for i, bookmark in enumerate(self.bookmarks, 1):
            url = bookmark['url']
            
            # Progress indicator
            if i % 10 == 0:
                print(f"Progress: {i}/{len(self.bookmarks)} ({i/len(self.bookmarks)*100:.1f}%)")
            
            try:
                response = session.head(url, timeout=timeout, allow_redirects=True)
                status_code = response.status_code
                
                bookmark_result = {
                    'title': bookmark['title'],
                    'url': url,
                    'status_code': status_code,
                    'domain': bookmark['domain']
                }
                
                if status_code == 404:
                    self.dead_links.append(bookmark_result)
                elif 200 <= status_code < 400:
                    self.working_links.append(bookmark_result)
                else:
                    bookmark_result['note'] = f'HTTP {status_code}'
                    self.dead_links.append(bookmark_result)
                    
            except requests.exceptions.RequestException as e:
                error_bookmark = {
                    'title': bookmark['title'],
                    'url': url,
                    'status_code': 'ERROR',
                    'error': str(e),
                    'domain': bookmark['domain']
                }
                self.dead_links.append(error_bookmark)
            
            # Small delay to be respectful to servers
            time.sleep(delay)
        
        print(f"Connectivity test complete!")
        print(f"Working links: {len(self.working_links)}")
        print(f"Dead/problematic links: {len(self.dead_links)}")
    
    def export_results(self):
        """Export results to CSV and JSON files"""
        print("Exporting results...")
        
        # Export dead links to CSV
        if self.dead_links:
            with open('dead_bookmarks.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['title', 'url', 'status_code', 'domain', 'error', 'note'])
                writer.writeheader()
                for link in self.dead_links:
                    writer.writerow(link)
            print(f"Exported {len(self.dead_links)} dead links to 'dead_bookmarks.csv'")
        
        # Export duplicates to CSV
        if self.duplicates:
            with open('duplicate_bookmarks.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Type', 'Details', 'Count'])
                
                for dup in self.duplicates:
                    if dup['type'] == 'duplicate_url':
                        details = f"URL: {dup['url']} | Titles: {', '.join(dup['titles'])}"
                    else:
                        details = f"Title: {dup['title']} | URLs: {', '.join(dup['urls'])}"
                    
                    writer.writerow([dup['type'], details, dup['count']])
            print(f"Exported {len(self.duplicates)} duplicate groups to 'duplicate_bookmarks.csv'")
        
        # Export working links to CSV
        if self.working_links:
            with open('working_bookmarks.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['title', 'url', 'status_code', 'domain'])
                writer.writeheader()
                writer.writerows(self.working_links)
            print(f"Exported {len(self.working_links)} working links to 'working_bookmarks.csv'")
        
        # Export complete results to JSON
        results = {
            'summary': {
                'total_bookmarks': len(self.bookmarks),
                'working_links': len(self.working_links),
                'dead_links': len(self.dead_links),
                'duplicates': len(self.duplicates)
            },
            'dead_links': self.dead_links,
            'duplicates': self.duplicates,
            'working_links': self.working_links
        }
        
        with open('bookmark_analysis.json', 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=2, ensure_ascii=False)
        print("Exported complete analysis to 'bookmark_analysis.json'")
    
    def print_summary(self):
        """Print a summary of results"""
        print("\n" + "="*50)
        print("BOOKMARK ANALYSIS SUMMARY")
        print("="*50)
        print(f"Total bookmarks processed: {len(self.bookmarks)}")
        print(f"Working links: {len(self.working_links)}")
        print(f"Dead/problematic links: {len(self.dead_links)}")
        print(f"Duplicate groups found: {len(self.duplicates)}")
        
        if self.dead_links:
            print(f"\nTop domains with dead links:")
            domain_counts = Counter(link.get('domain', 'Unknown') for link in self.dead_links)
            for domain, count in domain_counts.most_common(5):
                print(f"  {domain}: {count} dead links")
    
    def run(self):
        """Run the complete analysis"""
        self.parse_bookmarks()
        self.find_duplicates()
        self.test_connectivity()
        self.export_results()
        self.print_summary()

def main():
    # Check if bookmarks file is provided
    if len(sys.argv) != 2:
        print("Usage: python bookmark_organizer.py <bookmarks_file.html>")
        print("\nTo export bookmarks from Chrome:")
        print("1. Open Chrome")
        print("2. Go to Bookmarks > Bookmark Manager")
        print("3. Click the three dots menu > Export bookmarks")
        print("4. Save the HTML file and use it with this script")
        sys.exit(1)
    
    bookmarks_file = sys.argv[1]
    
    # Check if file exists
    if not Path(bookmarks_file).exists():
        print(f"Error: File '{bookmarks_file}' not found")
        sys.exit(1)
    
    # Run the organizer
    organizer = BookmarkOrganizer(bookmarks_file)
    organizer.run()

if __name__ == "__main__":
    main()