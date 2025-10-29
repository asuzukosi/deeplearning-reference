#!/usr/bin/env python3
"""
Dataset Builder - Google Images Scraper

A robust web scraper for downloading images from Google Images search results.
This tool is designed for building datasets for machine learning and computer vision projects.

Features:
- Downloads images from Google Images based on search queries
- Handles Google's anti-scraping measures
- Validates downloaded images to ensure quality
- Supports batch processing of multiple queries
- Configurable output directories and image counts

Author: AI Assistant
Date: 2024
"""

import argparse
import os
import re
import time
import urllib.parse
from typing import List, Set
from urllib.parse import urlparse

import requests
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class DatasetBuilder:
    """
    A class for scraping images from Google Images search results.
    
    This class provides methods to:
    - Set up a Chrome WebDriver with appropriate options
    - Navigate to Google Images and perform searches
    - Extract image URLs from search results
    - Download and validate images
    - Handle Google's anti-scraping measures
    """
    
    # CSS selectors for different Google Images layouts
    THUMBNAIL_SELECTORS = [
        "img.YQ4gaf",  # Main thumbnail selector
        "img.rg_i",    # Alternative thumbnail selector
        "img[data-src]",  # Thumbnails with data-src attribute
    ]
    
    FULL_IMAGE_SELECTORS = [
        "img.n3VNCb",  # Full-size image in preview
        "img.sFlh5c",  # Alternative full-size selector
        "img[data-src]",  # Full-size with data-src
    ]
    
    SHOW_MORE_SELECTORS = [
        "input[value='Show more results']",
        "button[aria-label='Show more results']",
        ".mye4qd",  # Show more button class
    ]
    
    COOKIE_BUTTON_SELECTORS = [
        "button[id='L2AGLb']",  # Accept all cookies button
        "button[aria-label*='Accept']",
        "button[aria-label*='accept']",
    ]
    
    def __init__(self, headless: bool = True):
        """
        Initialize the DatasetBuilder.
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
        """
        self.headless = headless
        self.driver = None
    
    def setup_driver(self) -> webdriver.Chrome:
        """
        Set up and configure Chrome WebDriver with appropriate options.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        chrome_options = webdriver.ChromeOptions()
        
        # Basic options for stability
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to appear more like a real browser
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable images for faster loading (we'll load them when needed)
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Run in headless mode if specified
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Initialize the driver
        self.driver = webdriver.Chrome(
            service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Execute script to remove webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return self.driver
    
    def accept_cookies(self, driver: webdriver.Chrome) -> None:
        """
        Accept cookie consent dialog if it appears.
        
        Args:
            driver (webdriver.Chrome): The webdriver instance
        """
        try:
            for selector in self.COOKIE_BUTTON_SELECTORS:
                try:
                    cookie_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if cookie_button.is_displayed():
                        cookie_button.click()
                        print("  Accepted cookies")
                        time.sleep(1)
                        break
                except:
                    # This selector didn't work, try the next one
                    continue
        except:
            # No cookie dialog found, which is fine
            pass
    
    def load_images_with_safe_scrolling(self, driver: webdriver.Chrome, count: int) -> None:
        """
        Load images with safe scrolling (no "Show more results" button clicking).
        
        Scrolling is safe, but clicking "Show more results" causes query changes.
        This method scrolls to load more images while avoiding the problematic button.
        
        Args:
            driver (webdriver.Chrome): the webdriver instance
            count (int): target number of images (for logging purposes)
        """
        print(f"loading images with safe scrolling (avoiding 'Show more results' button)...")
        
        # wait for initial images to load
        time.sleep(3)
        
        # get initial count
        initial_images = len(driver.find_elements(By.CSS_SELECTOR, "img"))
        print(f"  Initial images: {initial_images}")
        
        # scroll to load more images (but don't click "Show more results")
        max_scrolls = min(5, count // 10)  # limit scrolls to avoid issues
        for i in range(max_scrolls):
            # scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # count current images
            current_images = len(driver.find_elements(By.CSS_SELECTOR, "img"))
            print(f"  Scroll {i+1}/{max_scrolls}: Found {current_images} images")
            
            # if we have enough images, stop
            if current_images >= count * 2:  # 2x buffer for better selection
                break
        
        # final count
        final_images = len(driver.find_elements(By.CSS_SELECTOR, "img"))
        print(f"finished loading. total images available: {final_images}")
    
    def extract_image_urls(self, driver: webdriver.Chrome, count: int) -> List[str]:
        """
        Extract image URLs by clicking thumbnails and capturing full-size image URLs.
        
        This is the primary extraction method. It:
        1. Finds all thumbnail images on the page
        2. Clicks each thumbnail to open the full-size view
        3. Extracts the URL of the full-size image
        4. Handles Google's anti-scraping measures
        
        Args:
            driver (webdriver.Chrome): The webdriver instance
            count (int): Target number of image URLs to extract
            
        Returns:
            List[str]: List of extracted image URLs
        """
        print(f"extracting image URLs (target: {count})...")
        
        # find all thumbnail images using multiple selectors
        thumbnails = []
        for selector in self.THUMBNAIL_SELECTORS:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, selector)
            if thumbnails:
                print(f"Found {len(thumbnails)} thumbnails using selector: {selector}")
                break
        
        if not thumbnails:
            print("No thumbnails found")
            return []
        
        image_urls = set()
        
        # process available thumbnails without scrolling
        print(f"processing {len(thumbnails)} thumbnails...")
        
        for i, thumbnail in enumerate(thumbnails):
            try:
                # scroll thumbnail into view to avoid search bar interference
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", thumbnail)
                time.sleep(0.5)
                
                # click thumbnail using JavaScript to avoid interception
                driver.execute_script("arguments[0].click();", thumbnail)
                time.sleep(1)
                
                # look for full-size image using multiple selectors
                img_url = None
                for selector in self.FULL_IMAGE_SELECTORS:
                    try:
                        full_img = driver.find_element(By.CSS_SELECTOR, selector)
                        img_url = full_img.get_attribute("src")
                        if img_url and img_url.startswith("http"):
                            break
                    except:
                        continue
                
                # if no full image found, try data attributes
                if not img_url:
                    for attr in ["data-src", "data-original", "src"]:
                        try:
                            img_url = thumbnail.get_attribute(attr)
                            if img_url and img_url.startswith("http"):
                                break
                        except:
                            continue
                
                # handle Google thumbnail URLs (encrypted-tbn0.gstatic.com)
                if img_url and "encrypted-tbn0.gstatic.com" in img_url:
                    print(f"  [{i+1}] Found Google thumbnail URL, trying to find original...")
                    # try to get original URL from parent element
                    try:
                        parent = thumbnail.find_element(By.XPATH, "./..")
                        href = parent.get_attribute("href")
                        if href and "imgurl=" in href:
                            # extract original URL from href parameter
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            if "imgurl" in parsed:
                                img_url = parsed["imgurl"][0]
                                print(f"  [{i+1}] Found original URL from href: {img_url[:50]}...")
                    except:
                        pass
                    
                    # if still no original URL, try to find it in page source
                    if "encrypted-tbn0.gstatic.com" in img_url:
                        try:
                            page_source = driver.page_source
                            # look for the original URL in the page source
                            url_pattern = r'https?://[^"\s]+\.(?:jpg|jpeg|png|gif|webp)'
                            urls = re.findall(url_pattern, page_source)
                            if urls:
                                # take the first non-Google URL
                                for url in urls:
                                    if not any(domain in url for domain in ["gstatic.com", "googleusercontent.com"]):
                                        img_url = url
                                        print(f"  [{i+1}] Found original URL from page source: {img_url[:50]}...")
                                        break
                        except:
                            pass
                
                # only add if we have a valid URL and it's not a Google thumbnail
                if img_url and img_url.startswith("http") and "encrypted-tbn0.gstatic.com" not in img_url:
                    image_urls.add(img_url)
                    print(f"  [{i+1}] ✓ Found image URL: {img_url[:50]}...")
                else:
                    print(f"  [{i+1}] Could not find full image element")
                
            except StaleElementReferenceException:
                print(f"  [{i+1}] Stale element, skipping")
                continue
            except Exception as e:
                print(f"  [{i+1}] Error processing thumbnail: {str(e)[:100]}...")
                continue
        
        return list(image_urls)
    
    def extract_image_urls_from_page_source(self, driver: webdriver.Chrome, count: int) -> List[str]:
        """
        Alternative extraction method: parse URLs directly from page source HTML.
        
        This is a fallback method when the primary click-based extraction fails.
        It uses regular expressions to find image URLs in the page's HTML source.
        This is faster but may get lower-quality thumbnails instead of full images.
        
        Args:
            driver (webdriver.Chrome): The webdriver instance
            count (int): Target number of URLs to extract
            
        Returns:
            List[str]: List of image URLs found in page source
        """
        print("Trying alternative extraction method (page source parsing)...")
        image_urls = set()
        
        # get the entire HTML source of the page
        page_source = driver.page_source
        
        # regular expression patterns to match image URLs in the HTML
        # prioritize original URLs over thumbnails
        patterns = [
            # original image URLs (usually full-size) - highest priority
            r'"ou":"(https://[^"]+)"',
            
            # data-src attributes (lazy-loaded images)
            r'data-src="(https://[^"]+)"',
            
            # src attributes (direct image sources)
            r'src="(https://[^"]+)"',
            
            # general HTTP/HTTPS URLs that look like images
            r'https://[^"\s]+\.(?:jpg|jpeg|png|gif|webp)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, page_source)
            for match in matches:
                # filter out Google thumbnail URLs and other unwanted domains
                if (match.startswith("http") and 
                    len(match) > 20 and  # avoid very short URLs
                    not any(domain in match for domain in [
                        "gstatic.com", 
                        "googleusercontent.com",
                        "encrypted-tbn0.gstatic.com"
                    ])):
                    image_urls.add(match)
                    if len(image_urls) >= count:
                        break
            if len(image_urls) >= count:
                break
        
        # convert to list and limit to requested count
        result = list(image_urls)[:count]
        print(f"  ✓ Found {len(result)} URLs using page source parsing")
        return result
    
    def download_image(self, url: str, filename: str, output_dir: str) -> bool:
        """
        Download an image from a URL and save it to the specified directory.
        
        Args:
            url (str): URL of the image to download
            filename (str): Name to save the file as
            output_dir (str): Directory to save the file in
            
        Returns:
            bool: True if download was successful, False otherwise
        """
        try:
            # create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # set up headers to appear more like a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # download the image
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # validate the downloaded content
            content = response.content
            
            # check if content is too small (likely not a real image)
            if len(content) < 1000:
                print(f"  Image too small ({len(content)} bytes), likely corrupted")
                return False
            
            # check for common image file signatures
            image_signatures = [
                b'\xff\xd8\xff',  # JPEG
                b'\x89PNG\r\n\x1a\n',  # PNG
                b'GIF87a',  # GIF87a
                b'GIF89a',  # GIF89a
                b'RIFF',  # WebP (starts with RIFF)
            ]
            
            is_valid_image = any(content.startswith(sig) for sig in image_signatures)
            if not is_valid_image:
                print(f"  Invalid image format, likely HTML or error page")
                return False
            
            # save the image
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(content)
            
            # verify the file was saved correctly
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                print(f"  ✓ Downloaded: {filename}")
                return True
            else:
                print(f"  Failed to save file: {filename}")
                return False
                
        except Exception as e:
            print(f"  Failed to download {url}: {e}")
            return False
    
    def scrape_images(self, query: str, count: int = 10, output_dir: str = "results") -> int:
        """
        Main method to scrape images from Google Images.
        
        Args:
            query (str): Search query for images
            count (int): Number of images to download
            output_dir (str): Directory to save images
            
        Returns:
            int: Number of images successfully downloaded
        """
        print(f"🔍 Searching for: '{query}'")
        print(f"📊 Target: {count} images")
        print(f"📁 Output: {output_dir}")
        
        # set up the webdriver
        driver = self.setup_driver()
        
        try:
            # construct the Google Images search URL
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}&udm=2"
            print(f"🌐 Navigating to: {search_url}")
            
            # navigate to Google Images
            driver.get(search_url)
            time.sleep(2)
            
            # accept cookies if needed
            self.accept_cookies(driver)
            
            # load images with safe scrolling (no "Show more results" button)
            self.load_images_with_safe_scrolling(driver, count)
            
            # extract image URLs using primary method
            image_urls = self.extract_image_urls(driver, count)
            
            # if we didn't get enough URLs, try alternative method
            if len(image_urls) < count:
                print(f"only found {len(image_urls)} images with primary method.")
                print("trying alternative extraction method...")
                alternative_urls = self.extract_image_urls_from_page_source(driver, count)
                image_urls.extend(alternative_urls)
                # remove duplicates while preserving order
                image_urls = list(dict.fromkeys(image_urls))
            
            if not image_urls:
                print("❌ No image URLs found")
                return 0
            
            print(f"Successfully extracted {len(image_urls)} image URLs")
            
            # download the images
            print("\nDownloading images...")
            successful_downloads = 0
            
            for i, url in enumerate(image_urls[:count]):
                filename = f"{query.replace(' ', '_').lower()}_{i+1}.jpg"
                print(f"Downloading {i+1}/{count}: {filename}")
                
                if self.download_image(url, filename, output_dir):
                    successful_downloads += 1
            
            print(f"✅ Successfully downloaded {successful_downloads}/{count} images to '{output_dir}'")
            return successful_downloads
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            return 0
        finally:
            # always close the driver
            if driver:
                driver.quit()


def main():
    """Main function to run the scraper from command line."""
    parser = argparse.ArgumentParser(description="Download images from Google Images")
    parser.add_argument("query", help="Search query for images")
    parser.add_argument("--count", "-c", type=int, default=10, help="Number of images to download (default: 10)")
    parser.add_argument("--output", "-o", default="results", help="Output directory (default: results)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: True)")
    
    args = parser.parse_args()
    
    # create the scraper instance
    scraper = DatasetBuilder(headless=args.headless)
    
    # run the scraper
    successful_downloads = scraper.scrape_images(args.query, args.count, args.output)
    
    # exit with appropriate code
    exit(0 if successful_downloads > 0 else 1)


if __name__ == "__main__":
    main()