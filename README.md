# Project 5: Web Scraper (News & Blog Headline Extractor)

A clean, beginner-friendly, and professional Python web scraper that extracts headlines from publicly accessible news/blog webpages and saves them into a structured CSV file.

---

## Table of Contents
- [Project Description](#project-description)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation Instructions](#installation-instructions)
- [How to Run](#how-to-run)
- [Scraping Workflow](#scraping-workflow)
- [CSV Output Explanation](#csv-output-explanation)
- [Responsible Scraping & robots.txt Note](#responsible-scraping--robotstxt-note)
- [Example Output](#example-output)
- [Testing Instructions](#testing-instructions)
- [License](#license)

---

## Project Description

As part of **Internship Project 5**, this tool demonstrates foundational web scraping techniques in Python. It fetches live HTML content from a public news aggregator ([Hacker News](https://news.ycombinator.com/)), extracts story titles and destination links, attaches metadata such as timestamp and source URL, and exports the clean dataset to a `headlines.csv` file using standard library utilities.

The scraper is built with ethics, robustness, and simplicity in mind: it respects `robots.txt` guidelines, adds polite delays between requests, and handles network or HTTP exceptions gracefully without crashing.

---

## Features

- **Robots.txt Compliance**: Automatically inspects the target website's `robots.txt` using `urllib.robotparser` before requesting content.
- **Polite Rate Limiting**: Employs `time.sleep()` to prevent server load spikes.
- **Targeted & Fallback Parsing**:
  - Primary parser optimized for news aggregator layouts (`span.titleline`).
  - Fallback parser for generic blog/article headings (`h1`, `h2`, `h3` tags).
- **Graceful Error Handling**: Manages malformed URLs, DNS resolution failures, connection timeouts, HTTP error codes (403, 404, 500), and pages without headlines.
- **Clean CSV Export**: Outputs comma-separated files encoded in `UTF-8` using Python's built-in `csv` module, preserving special characters and formatting.
- **Command-Line Interface (CLI)**: Out of the box, zero arguments are needed, but optional flags `--url`, `--output`, and `--delay` are supported.

---

## Technologies Used

- **Python 3.10+**: Core programming language.
- **Requests**: HTTP library for sending GET requests and downloading HTML markup.
- **BeautifulSoup4 (bs4)**: HTML parsing library for traversing the DOM and extracting elements.
- **urllib.robotparser & urllib.parse**: Built-in standard library modules for robots exclusion protocol checking and URL handling.
- **csv**: Built-in Python library for writing structured data into CSV spreadsheets.
- **argparse**: Built-in CLI argument parsing.

---

## Project Structure

```text
web-scraper/
│
├── web_scraper.py      # Main Python scraper application
├── headlines.csv       # Extracted headlines dataset (generated upon run)
├── requirements.txt    # Project dependencies (requests, beautifulsoup4)
├── .gitignore          # Git exclusion rules for virtual environments & cache
└── README.md           # Comprehensive project documentation
```

---

## Installation Instructions

### Prerequisites
Make sure you have Python installed (Python 3.8 or higher is recommended). Check via:
```bash
python --version
```

### 1. Clone or Open Workspace
Navigate to your project directory:
```bash
cd "c:\Users\patipatti lalitha\Downloads\web scrapper"
```

### 2. (Optional) Create and Activate a Virtual Environment
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install the required packages using `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## How to Run

### Basic Usage (Recommended)
Run the script with default settings (scrapes Hacker News and saves 30 headlines to `headlines.csv`):
```bash
python web_scraper.py
```

### Advanced Usage (Command-Line Arguments)
Customize target URL, output filename, or request delay:
```bash
python web_scraper.py --url "https://news.ycombinator.com/" --output "my_headlines.csv" --delay 2.0
```

#### Available Flags:
- `--url`: Target webpage URL (default: `https://news.ycombinator.com/`)
- `--output`: Path to output CSV file (default: `headlines.csv`)
- `--delay`: Delay in seconds before fetching (default: `1.5`)

---

## Scraping Workflow

The scraping process follows a structured 5-step pipeline:

```text
[ 1. URL Validation ]
       │
       ▼
[ 2. robots.txt Check ] ──(Disallowed)──> Log warning & stop gracefully
       │
   (Allowed)
       ▼
[ 3. Polite Delay & Fetch ] ──(HTTP/Net Error)──> Log error & stop gracefully
       │
    (HTTP 200)
       ▼
[ 4. BeautifulSoup HTML Parsing ] ──(No headlines)──> Log notice & exit cleanly
       │
 (Found Headlines)
       ▼
[ 5. CSV Export (utf-8) ] ──> headlines.csv generated
```

1. **URL Validation**: Verifies that the URL is a syntactically correct HTTP/HTTPS address.
2. **Robots Permission Check**: Fetches `https://domain.com/robots.txt` and evaluates whether the scraper's user agent is allowed to access the target path.
3. **HTTP Fetch**: Waits for the specified delay (`time.sleep()`), sets appropriate request headers (e.g., standard browser User-Agent), and performs `requests.get()`.
4. **HTML Parsing**: BeautifulSoup parses the markup with `html.parser` and extracts headline strings, links, source URL, and timestamp.
5. **CSV Generation**: The extracted data is written into `headlines.csv` with standard headers.

---

## CSV Output Explanation

The generated `headlines.csv` contains the following structured fields:

| Field Name | Description | Example Value |
| :--- | :--- | :--- |
| `headline` | Title of the news article or blog post | `"Why don't more developers 'use the platform'?"` |
| `article_url` | Direct hyperlink to the full story or discussion | `https://nolanlawson.com/2026/10/03/why-dont-more-developers-use-the-platform/` |
| `source_url` | Webpage URL where the headline was scraped from | `https://news.ycombinator.com/` |
| `scraped_at` | UTC timestamp indicating when extraction occurred | `2026-10-04 07:20:57 UTC` |

---

## Responsible Scraping & robots.txt Note

This project adheres to ethical web scraping best practices:

1. **Robots Exclusion Protocol**: Web scrapers should always inspect `/robots.txt`. If a site administrator explicitly disallows scraping (`Disallow: /`), the script terminates immediately without sending scrape requests.
2. **Polite Request Rates**: A configurable delay (`time.sleep()`) is added before requests to avoid overburdening web servers.
3. **Public Content Only**: Only publicly accessible webpages are scraped. The scraper **does not**:
   - Access private, login-protected, or paywalled content.
   - Bypass CAPTCHAs, bot-detection tools, or Cloudflare challenges.
   - Harvest personally identifiable information (PII).

---

## Example Output

### Terminal Execution Output:
```text
============================================================
 WEB SCRAPER: News & Blog Headline Extractor
============================================================
Target URL : https://news.ycombinator.com/
Output CSV : headlines.csv
Delay      : 1.5s
------------------------------------------------------------
[robots.txt] Scraping permitted for 'https://news.ycombinator.com/' according to https://news.ycombinator.com/robots.txt.
[Rate Limit] Pausing for 1.5 second(s) before requesting https://news.ycombinator.com/...
[Fetching] Requesting webpage: https://news.ycombinator.com/
[Extracted] Found 30 headlines successfully.
[CSV] Successfully saved 30 headlines to 'headlines.csv'.
------------------------------------------------------------
[Completed] Scraper finished successfully. Total headlines saved: 30
============================================================
```

### Sample CSV Content (`headlines.csv`):
```csv
headline,article_url,source_url,scraped_at
"Why don't more developers ""use the platform""?",https://nolanlawson.com/2026/10/03/why-dont-more-developers-use-the-platform/,https://news.ycombinator.com/,2026-10-04 07:20:57 UTC
Tell HN: Bob Cringely has died,https://news.ycombinator.com/item?id=49949438,https://news.ycombinator.com/,2026-10-04 07:20:57 UTC
So you think you could be an electrician?,https://asteriskmag.com/issues/15/so-you-think-you-could-be-an-electrician,https://news.ycombinator.com/,2026-10-04 07:20:57 UTC
```

---

## Testing Instructions

To verify that the project meets all internship criteria, execute the following tests:

### 1. Default Scraping Test
Run the primary scraper test to verify headline extraction and CSV creation:
```bash
python web_scraper.py
```
**Expected Result**: Status messages will display progress, and a fresh `headlines.csv` with 30 headlines will be generated.

### 2. Verify Generated CSV File
Inspect the top rows and row count:
```bash
python -c "import csv; f = list(csv.DictReader(open('headlines.csv', encoding='utf-8'))); print('Total rows:', len(f)); print('First headline:', f[0]['headline'])"
```
**Expected Result**: Displays `Total rows: 30` and the first headline.

### 3. Invalid URL Test
Test scraper behavior when given an invalid URL:
```bash
python web_scraper.py --url "invalid-domain"
```
**Expected Result**: Prints an error message regarding invalid URL format and exits without crashing.

### 4. Robots.txt Disallow Test
Test scraper behavior on a domain that disallows web scraping:
```bash
python web_scraper.py --url "https://lobste.rs"
```
**Expected Result**: Detects the restriction from `robots.txt` and stops execution gracefully.

### 5. HTTP Error Test (404 Not Found)
Test response handling on a non-existent page:
```bash
python web_scraper.py --url "https://httpbin.org/status/404"
```
**Expected Result**: Reports `HTTP status 404 (NOT FOUND)` and aborts without throwing unhandled exceptions.

---

## License
This project is developed for educational purposes as part of the Web Scraping Internship Project.
