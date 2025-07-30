# Chrome Bookmarks Organizer

A Python script that helps you clean up your Chrome bookmarks by finding duplicates and testing link connectivity.

## Features

- 🔍 **Find Duplicates**: Identifies duplicate URLs and similar bookmark titles
- 🌐 **Test Connectivity**: Checks if bookmarks are still accessible (finds 404s)
- 📊 **Export Results**: Generates CSV and JSON reports for easy analysis
- 📈 **Domain Analysis**: Shows which domains have the most dead links

## Installation

1. Clone this repository:
```cmd
git clone https://github.com/yourusername/bookmark-organizer.git
cd bookmark-organizer
```

2. Install Python dependencies:
```cmd
pip install -r requirements.txt
```

## Usage

### Export Chrome Bookmarks
1. Open Chrome
2. Go to **Bookmarks** → **Bookmark Manager** (or press `Ctrl+Shift+O`)
3. Click the **three dots menu** → **Export bookmarks**
4. Save the HTML file to your bookmark-organizer folder

### Run the Script
```cmd
python bookmark_organizer.py bookmarks.html
```

## Output Files

The script generates several files in the same directory:

- `dead_bookmarks.csv` - Bookmarks that return 404 or connection errors
- `duplicate_bookmarks.csv` - Duplicate bookmarks found
- `working_bookmarks.csv` - All working links with status codes
- `bookmark_analysis.json` - Complete analysis in JSON format

## Example Output

```
BOOKMARK ANALYSIS SUMMARY
==================================================
Total bookmarks processed: 1,247
Working links: 1,156
Dead/problematic links: 91
Duplicate groups found: 23

Top domains with dead links:
  old-site.com: 15 dead links
  archived-blog.net: 8 dead links
  ...
```

## Windows-Specific Notes

- Make sure Python is installed and added to your PATH
- You can double-click the `.py` file to run it if Python is properly configured
- Output files will be created in the same folder as the script

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - see LICENSE file for details