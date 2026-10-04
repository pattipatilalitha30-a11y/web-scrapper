"""
Web Scraper - News & Blog Headline Extractor
=============================================
Project 5: Internship Task

A professional, clean, and beginner-friendly Python web scraper that extracts
headlines from a publicly accessible news/blog webpage and saves them into a CSV file.

Key Features:
- Respects website robots.txt before making requests.
- Polite scraping with configurable delay (time.sleep).
- Graceful error handling for invalid URLs, network/HTTP issues, and empty pages.
- Saves structured data (headline, article_url, source_url, scraped_at) using csv.
- Uses requests and BeautifulSoup4 (soup.find_all).
"""

import argparse
import csv
from datetime import datetime, timezone
import sys
import time
import urllib.parse
import urllib.robotparser
from bs4 import BeautifulSoup
import requests


# Default demo target URL (publicly accessible news aggregator)
DEFAULT_URL = "https://news.ycombinator.com/"
DEFAULT_OUTPUT_CSV = "headlines.csv"
DEFAULT_DELAY = 1.5  # seconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def is_valid_url(url: str) -> bool:
    """
    Validates whether the provided string is a valid HTTP/HTTPS URL.
    
    Args:
        url: URL string to validate.
        
    Returns:
        bool: True if the URL has a valid scheme and network location, False otherwise.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def is_allowed_by_robots(url: str, user_agent: str = "*", timeout: int = 10) -> bool:
    """
    Checks the website's robots.txt rules to ensure scraping is permitted.
    
    Args:
        url: The webpage URL intended to be scraped.
        user_agent: User-Agent string to check against robots.txt.
        timeout: Network timeout in seconds for fetching robots.txt.
        
    Returns:
        bool: True if scraping is allowed or robots.txt doesn't disallow it;
              False if explicitly forbidden.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        headers = {"User-Agent": USER_AGENT}
        response = requests.get(robots_url, headers=headers, timeout=timeout)
        
        # If robots.txt does not exist (404), crawling is permitted by standard convention
        if response.status_code == 404:
            print(f"[robots.txt] No robots.txt found at {robots_url} (HTTP 404). Access allowed.")
            return True
        elif response.status_code in (401, 403):
            print(f"[robots.txt] Access to {robots_url} forbidden (HTTP {response.status_code}).")
            return False
            
        parser = urllib.robotparser.RobotFileParser()
        parser.parse(response.text.splitlines())
        
        allowed = parser.can_fetch(user_agent, url)
        if allowed:
            print(f"[robots.txt] Scraping permitted for '{url}' according to {robots_url}.")
        else:
            print(f"[robots.txt] Warning: Scraping disallowed for '{url}' according to {robots_url}.")
        return allowed
        
    except requests.exceptions.RequestException as e:
        print(f"[robots.txt] Could not retrieve robots.txt ({e}). Proceeding cautiously.")
        return True
    except Exception as e:
        print(f"[robots.txt] Error evaluating robots.txt ({e}). Proceeding cautiously.")
        return True


def fetch_webpage(url: str, delay: float = DEFAULT_DELAY, timeout: int = 10) -> str | None:
    """
    Fetches the HTML content of a webpage using requests.
    Includes a polite delay before request and handles network errors gracefully.
    
    Args:
        url: The webpage URL to fetch.
        delay: Delay in seconds to pause before sending the request.
        timeout: Request timeout in seconds.
        
    Returns:
        str | None: Raw HTML content string if successful, or None on failure.
    """
    if not is_valid_url(url):
        print(f"[Error] Invalid URL provided: '{url}'. Please include http:// or https://")
        return None

    # Polite delay to avoid hammering the server
    if delay > 0:
        print(f"[Rate Limit] Pausing for {delay:.1f} second(s) before requesting {url}...")
        time.sleep(delay)

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        print(f"[Fetching] Requesting webpage: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        
        # Check HTTP response status
        if response.status_code != 200:
            print(f"[Error] Server returned HTTP status {response.status_code} ({response.reason}) for {url}")
            return None
            
        return response.text

    except requests.exceptions.Timeout:
        print(f"[Error] Connection timed out while requesting {url}")
    except requests.exceptions.ConnectionError:
        print(f"[Error] Network connection failed or domain could not be reached: {url}")
    except requests.exceptions.HTTPError as http_err:
        print(f"[Error] HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"[Error] An error occurred during request: {err}")
    except Exception as e:
        print(f"[Error] Unexpected error while fetching webpage: {e}")

    return None


def extract_headlines(html: str, source_url: str) -> list[dict]:
    """
    Parses the HTML and extracts headlines using BeautifulSoup.
    
    Args:
        html: Raw HTML content string.
        source_url: The source URL where this HTML was fetched from.
        
    Returns:
        list[dict]: List of dictionaries containing headline metadata.
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    headlines_data = []
    scraped_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Strategy 1: Targeted parsing for Hacker News (span.titleline)
    hn_spans = soup.find_all("span", class_="titleline")
    if hn_spans:
        for span in hn_spans:
            anchor = span.find("a")
            if anchor:
                title = anchor.get_text(strip=True)
                href = anchor.get("href", "").strip()
                # Resolve relative URLs
                full_url = urllib.parse.urljoin(source_url, href) if href else source_url
                if title:
                    headlines_data.append({
                        "headline": title,
                        "article_url": full_url,
                        "source_url": source_url,
                        "scraped_at": scraped_timestamp,
                    })
        if headlines_data:
            return headlines_data

    # Strategy 2: Generic fallback for other news/blog sites (h1, h2, h3 tags)
    heading_tags = soup.find_all(["h1", "h2", "h3"])
    seen_titles = set()
    
    for tag in heading_tags:
        title = tag.get_text(strip=True)
        # Filter out common empty, navigation, or excessively short headers
        if not title or len(title) < 10 or len(title) > 300:
            continue
        if title in seen_titles:
            continue
            
        # Check if the tag contains or is wrapped in an anchor link
        anchor = tag.find("a") or tag.find_parent("a")
        href = anchor.get("href", "").strip() if anchor else ""
        full_url = urllib.parse.urljoin(source_url, href) if href else source_url

        seen_titles.add(title)
        headlines_data.append({
            "headline": title,
            "article_url": full_url,
            "source_url": source_url,
            "scraped_at": scraped_timestamp,
        })

    return headlines_data


def save_headlines_to_csv(headlines: list[dict], output_file: str = DEFAULT_OUTPUT_CSV) -> bool:
    """
    Saves the extracted headlines into a CSV file using Python's built-in csv module.
    
    Args:
        headlines: List of headline dictionaries.
        output_file: Destination path for the CSV file.
        
    Returns:
        bool: True if writing succeeded, False otherwise.
    """
    if not headlines:
        print("[CSV] No headlines to save. Skipping CSV file creation.")
        return False

    fieldnames = ["headline", "article_url", "source_url", "scraped_at"]

    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(headlines)
            
        print(f"[CSV] Successfully saved {len(headlines)} headlines to '{output_file}'.")
        return True
    except IOError as e:
        print(f"[Error] Failed to write headlines to CSV file '{output_file}': {e}")
        return False


def run_scraper(url: str, output_csv: str = DEFAULT_OUTPUT_CSV, delay: float = DEFAULT_DELAY) -> list[dict]:
    """
    Orchestrates the complete web scraping process:
    1. Validates the URL.
    2. Checks robots.txt permission.
    3. Fetches the page content with rate-limiting delay.
    4. Parses HTML and extracts headlines using BeautifulSoup.
    5. Saves results to a CSV file.
    
    Args:
        url: Target news/blog webpage URL.
        output_csv: Filename or path for the resulting CSV.
        delay: Delay in seconds to pause before requesting.
        
    Returns:
        list[dict]: List of extracted headline dictionaries.
    """
    print("=" * 60)
    print(" WEB SCRAPER: News & Blog Headline Extractor")
    print("=" * 60)
    print(f"Target URL : {url}")
    print(f"Output CSV : {output_csv}")
    print(f"Delay      : {delay}s")
    print("-" * 60)

    # Step 1: Validate URL
    if not is_valid_url(url):
        print(f"[Error] Invalid URL format: '{url}'. Please provide a valid URL (http/https).")
        return []

    # Step 2: Check robots.txt permissions
    if not is_allowed_by_robots(url):
        print(f"[Disallowed] Scraping '{url}' is restricted by the website's robots.txt policy.")
        print("[Disallowed] Aborting scraper to respect website guidelines.")
        return []

    # Step 3: Fetch HTML
    html_content = fetch_webpage(url, delay=delay)
    if not html_content:
        print("[Warning] Could not retrieve HTML content. No headlines extracted.")
        return []

    # Step 4: Extract headlines with BeautifulSoup
    headlines = extract_headlines(html_content, source_url=url)
    if not headlines:
        print("[Warning] Webpage retrieved successfully, but no headlines were found.")
        print("          The page might use dynamic JavaScript rendering or custom markup.")
        return []

    print(f"[Extracted] Found {len(headlines)} headlines successfully.")

    # Step 5: Save to CSV
    save_headlines_to_csv(headlines, output_file=output_csv)

    print("-" * 60)
    print(f"[Completed] Scraper finished successfully. Total headlines saved: {len(headlines)}")
    print("=" * 60)
    return headlines


def main():
    """
    Main entry point for command-line execution.
    """
    parser = argparse.ArgumentParser(
        description="Extract headlines from a public news/blog webpage and export to CSV."
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help=f"Target webpage URL to scrape (default: {DEFAULT_URL})"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_CSV,
        help=f"Output CSV file path (default: {DEFAULT_OUTPUT_CSV})"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay in seconds before fetching (default: {DEFAULT_DELAY}s)"
    )

    args = parser.parse_args()
    
    extracted = run_scraper(url=args.url, output_csv=args.output, delay=args.delay)
    
    if not extracted:
        # Exit with status 1 if scraping yielded nothing due to error/disallow
        sys.exit(1)


if __name__ == "__main__":
    main()
