# !/usr/bin/env python3

import asyncio
from playwright.async_api import async_playwright

AUTH = 'brd-customer-hl_6bb8cf74-zone-scrape:wqlqa3bt8we4'
TARGET_URL = 'https://www.booking.com/'

async def main():
    print('Connecting to Browser...')
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(
            f'wss://{AUTH}@brd.superproxy.io:9222'
        )
        page = await browser.new_page()
        
        # Get debugging URL
        client = await page.context.new_cdp_session(page)
        frame_tree = await client.send('Page.getFrameTree')
        frame_id = frame_tree['frameTree']['frame']['id']
        inspect_result = await client.send('Page.inspect', {'frameId': frame_id})
        print(f"Debug URL: {inspect_result['url']}")
        
        # Navigate to target
        await page.goto(TARGET_URL)

        print(await page.content())
        await page.screenshot(path='screenshot.png', full_page=True)
        print('Navigation complete!')
        
        await browser.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'Error: {e}')