#!/usr/bin/env python3

import asyncio
import json
import re
import time
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from playwright.async_api import Page, async_playwright

AUTH = 'brd-customer-hl_6bb8cf74-zone-scrape:wqlqa3bt8we4'
BROWSER_WS = f'wss://{AUTH}@brd.superproxy.io:9222'
SEARCH_TEXT = 'bangkok'
TARGET_URL = f'https://www.instagram.com/explore/search/keyword/?q=%23{SEARCH_TEXT}'

USE_REMOTE_BROWSER = False  # Set True to connect via proxy WS; False to launch a local headed browser
HEADLESS = False

INSTAGRAM_BASE_URL = 'https://www.instagram.com'
INSTAGRAM_POST_RE = re.compile(r'^/p/[A-Za-z0-9_-]+/?$')
INSTAGRAM_FULL_URL_RE = re.compile(r'^https?://(?:www\.)?instagram\.com/p/[A-Za-z0-9_-]+/?$')


def normalize_instagram_post_url(url: str, base_url: str = INSTAGRAM_BASE_URL) -> Optional[str]:
    if not url:
        return None

    if url.startswith('//'):
        url = 'https:' + url
    if url.startswith('/'):
        url = urljoin(base_url, url)

    parsed = urlparse(url)
    if parsed.netloc not in ('www.instagram.com', 'instagram.com'):
        return None

    path = parsed.path.rstrip('/')
    if not path.startswith('/p/'):
        return None

    return f'https://www.instagram.com{path}/'


def extract_instagram_post_urls_from_html(html: str, base_url: str = INSTAGRAM_BASE_URL) -> List[str]:
    urls = set()

    for href in re.findall(r'href=["\']([^"\']+)["\']', html):
        normalized = normalize_instagram_post_url(href, base_url)
        if normalized:
            urls.add(normalized)

    for raw_url in re.findall(r'https?://(?:www\.)?instagram\.com/p/[A-Za-z0-9_-]+/?', html):
        normalized = normalize_instagram_post_url(raw_url, base_url)
        if normalized:
            urls.add(normalized)

    return sorted(urls)


async def extract_instagram_post_urls(page: Page, base_url: str = INSTAGRAM_BASE_URL) -> List[str]:
    anchors = await page.query_selector_all('a[href*="/p/"]')
    urls = set()

    for anchor in anchors:
        href = await anchor.get_attribute('href')
        normalized = normalize_instagram_post_url(href, base_url)
        if normalized:
            urls.add(normalized)

    return sorted(urls)


async def scrape_instagram_posts_from_url(url: str) -> List[str]:
    async with async_playwright() as p:
        if USE_REMOTE_BROWSER:
            browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        else:
            browser = await p.chromium.launch(headless=HEADLESS)

        page = await browser.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            post_urls = await extract_instagram_post_urls(page)
            await asyncio.sleep(60)
            return post_urls
        finally:
            await browser.close()


def extract_instagram_post_urls_from_file(file_path: Path) -> List[str]:
    html = file_path.read_text(encoding='utf-8')
    return extract_instagram_post_urls_from_html(html)


def save_post_urls(post_urls: List[str], search_text: str) -> Path:
    directory = Path(__file__).resolve().parent / search_text
    directory.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    output_file = directory / f'{timestamp}.json'
    output_file.write_text(json.dumps(post_urls, indent=2, ensure_ascii=False), encoding='utf-8')

    return output_file


async def main():
    html_file = Path(__file__).resolve().parent / '#bangkok • Instagram.html'
    if html_file.exists():
        post_urls = extract_instagram_post_urls_from_file(html_file)
    else:
        print('Connecting to browser...')
        post_urls = await scrape_instagram_posts_from_url(TARGET_URL)

    output_file = save_post_urls(post_urls, SEARCH_TEXT)
    print(f'Saved {len(post_urls)} post URLs to {output_file}')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'Error: {e}')
