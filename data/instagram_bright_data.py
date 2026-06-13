#!/usr/bin/env python3

import json
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, List, Optional
from urllib.parse import urljoin, urlparse

SEARCH_TEXT = 'bangkok'
HTML_FILE = Path(__file__).resolve().parent / 'Instagram.html'
RESPONSE_DIR = Path(__file__).resolve().parent / 'response'
BRIGHTDATA_DATASET_ID = 'gd_lk5ns7kz21pck8jpis'
# BRIGHTDATA_API_KEY = os.getenv('BRIGHTDATA_API_KEY', 'YOUR_API_KEY')
BRIGHTDATA_API_KEY='120275e4-f652-43fd-aa4a-7a00cfdcfc63';
BRIGHTDATA_URL = f'https://api.brightdata.com/datasets/v3/scrape?dataset_id={BRIGHTDATA_DATASET_ID}&include_errors=true'

INSTAGRAM_BASE_URL = 'https://www.instagram.com'
INSTAGRAM_POST_RE = re.compile(r'^/p/[A-Za-z0-9_-]+/?$')
INSTAGRAM_FULL_URL_RE = re.compile(r'^https?://(?:www\.)?instagram\.com/p/[A-Za-z0-9_-]+/?$')


def pretty_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


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


def send_brightdata_request(input_urls: List[str], output_name: str) -> Path:
    # if BRIGHTDATA_API_KEY == 'YOUR_API_KEY':
    #     raise ValueError('Set BRIGHTDATA_API_KEY in your environment before running this script.')

    payload = {'input': [{'url': url} for url in input_urls]}
    payload_text = pretty_json(payload)
    print('Bright Data payload:')
    print(payload_text)
    request_body = payload_text.encode('utf-8')
    request = urllib.request.Request(
        BRIGHTDATA_URL,
        data=request_body,
        headers={
            'Authorization': f'Bearer {BRIGHTDATA_API_KEY}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    RESPONSE_DIR.mkdir(parents=True, exist_ok=True)
    response_file = RESPONSE_DIR / f'{output_name}.response.json'

    with urllib.request.urlopen(request, timeout=120) as response:
        response_text = response.read().decode('utf-8')

    try:
        response_data = json.loads(response_text)
        pretty_response_text = pretty_json(response_data)
    except json.JSONDecodeError:
        pretty_response_text = response_text

    response_file.write_text(pretty_response_text, encoding='utf-8')

    return response_file


def main():
    if HTML_FILE.exists():
        print(f'Reading saved HTML from {HTML_FILE}')
        post_urls = extract_instagram_post_urls_from_file(HTML_FILE)
    else:
        raise FileNotFoundError(f'Instagram HTML file not found: {HTML_FILE}')

    output_file = save_post_urls(post_urls, SEARCH_TEXT)
    print(f'Saved {len(post_urls)} post URLs to {output_file}')

    if not post_urls:
        print('No Instagram post URLs found; skipping Bright Data request.')
        return

    response_file = send_brightdata_request(post_urls, output_file.stem)
    print(f'Saved Bright Data response to {response_file}')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Error: {e}')
