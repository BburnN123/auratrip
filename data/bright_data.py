#!/usr/bin/env python3

import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

AUTH = 'brd-customer-hl_6bb8cf74-zone-scrape:wqlqa3bt8we4'
BROWSER_WS = f'wss://{AUTH}@brd.superproxy.io:9222'
SEARCH_TEXT = 'bangkok'
TARGET_URL = f'https://www.instagram.com/explore/search/keyword/?q=%23{SEARCH_TEXT}'

USE_REMOTE_BROWSER = False  # Set True to connect via proxy WS; False to launch a local headed browser
HEADLESS = False


def add_days(date: datetime, days: int) -> datetime:
    return date + timedelta(days=days)


def to_booking_timestamp(date: datetime) -> str:
    return date.strftime('%Y-%m-%d')


async def close_popup(page):
    try:
        close_btn = await page.wait_for_selector('[aria-label="Dismiss sign-in info."]', timeout=25000, state='visible')
        print('Popup appeared! Closing...')
        await close_btn.click()
        await page.wait_for_timeout(500)
        print('Popup closed!')
    except Exception:
        print("Popup didn't appear or could not be closed.")


async def select_destination(page, search_text):
    print('Waiting for search field...')
    search_input = await page.wait_for_selector('[data-testid="destination-container"] input', timeout=60000)
    print('Filling destination...')
    await search_input.fill(search_text)
    await page.wait_for_timeout(500)
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('Enter')


async def select_dates(page, check_in, check_out):
    print('Opening date picker...')
    await page.click('[data-testid="searchbox-dates-container"]')
    await page.wait_for_selector('[data-testid="searchbox-datepicker-calendar"]', timeout=60000)
    print(f'Selecting dates {check_in} to {check_out}...')
    await page.click(f'[data-date="{check_in}"]')
    await page.click(f'[data-date="{check_out}"]')


async def search_booking(page, search_text, check_in, check_out):
    await select_destination(page, search_text)
    await select_dates(page, check_in, check_out)
    print('Submitting search...')
    await PromiseAllNavigation(page)


async def PromiseAllNavigation(page):
    await asyncio.gather(
        page.click('button[type="submit"]'),
        page.wait_for_navigation(wait_until='domcontentloaded', timeout=60000),
    )


async def parse_results(page):
    await page.wait_for_selector('[data-testid="property-card"]', timeout=60000)
    cards = await page.query_selector_all('[data-testid="property-card"]')
    results = []

    for card in cards:
        name = await card.eval_on_selector('[data-testid="title"]', 'el => el.textContent.trim()', strict=False)
        price = await card.eval_on_selector('[data-testid="price-and-discounted-price"]', 'el => el.textContent.trim()', strict=False)
        review_score = await card.eval_on_selector('[data-testid="review-score"]', 'el => el.textContent.trim()', strict=False) or ''

        score = ''
        reviews = ''
        if review_score:
            parts = review_score.split('\n')
            score = float(parts[0]) if parts and parts[0].replace('.', '', 1).isdigit() else parts[0]
            if len(parts) > 1:
                reviews = int(''.join(ch for ch in parts[-1] if ch.isdigit())) if any(ch.isdigit() for ch in parts[-1]) else parts[-1]

        results.append({
            'name': name,
            'price': price,
            'score': score,
            'reviews': reviews,
        })

    return results


async def main():
    now = datetime.utcnow()
    check_in = to_booking_timestamp(add_days(now, 1))
    check_out = to_booking_timestamp(add_days(now, 2))

    print('Connecting to browser...')
    async with async_playwright() as p:
        if USE_REMOTE_BROWSER:
            browser = await p.chromium.connect_over_cdp(BROWSER_WS)
        else:
            browser = await p.chromium.launch(headless=HEADLESS)
        page = await browser.new_page()

        try:
            print('Navigating to Booking.com...')
            await page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=60000)

            await close_popup(page)
            await select_destination(page, SEARCH_TEXT)
            await select_dates(page, check_in, check_out)
            print('Submitting search and waiting for results...')
            await asyncio.gather(
                page.click('button[type="submit"]'),
                page.wait_for_navigation(wait_until='domcontentloaded', timeout=60000),
            )
            if not HEADLESS:
                print('Running in headed mode; browser window should be visible.')

            print('Parsing data...')
            data = await parse_results(page)
            print(json.dumps(data, indent=2, ensure_ascii=False))

            await page.screenshot(path='booking_search.png', full_page=True)
        except Exception as e:
            print(f'Error during run: {e}')
            try:
                await page.screenshot(path='booking_error.png', full_page=True)
                print('Saved error screenshot to booking_error.png')
            except Exception as screenshot_error:
                print(f'Failed to capture error screenshot: {screenshot_error}')
            raise
        finally:
            await browser.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f'Error: {e}')
