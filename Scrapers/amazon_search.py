import asyncio
from playwright.async_api import async_playwright
import csv
from urllib.parse import quote_plus

async def amazon_search_scraper(keyword='shirts', page_count=2, output='data/amazon_search.csv'):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        for page_num in range(1, page_count + 1):
            url = f'https://www.amazon.in/s?k={quote_plus(keyword)}&page={page_num}'
            print(f"🔍 Navigating to: {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)

            items = await page.locator("div.s-result-item[data-component-type='s-search-result']").all()
            print(f"➡️ Found {len(items)} products on page {page_num}")

            for item in items:
                try:
                    title = await item.locator("div.s-title-instructions-style >> a").inner_text()
                    rel_url = await item.locator("div.s-title-instructions-style >> a").get_attribute("href")
                    product_url = f"https://www.amazon.in{rel_url.split('?')[0]}"
                    asin = rel_url.split("/")[3] if rel_url and len(rel_url.split("/")) > 3 else None

                    price = await item.locator("span.a-price-whole").first.inner_text() if await item.locator("span.a-price-whole").count() else 'NA'
                    real_price = await item.locator("span.a-price.a-text-price span:nth-child(2)").first.inner_text() if await item.locator("span.a-price.a-text-price span:nth-child(2)").count() else 'NA'

                    rating = await item.locator("div.a-section.a-spacing-none.a-spacing-top-micro a span").first.inner_text() 
                    prime_icon = item.locator("div.a-row.s-align-children-center i.a-icon.a-icon-prime")
                    is_prime = await prime_icon.count() > 0
                    results.append({
                        "keyword": keyword,
                        "asin": asin,
                        "url": product_url,
                        "ad": "/slredirect/" in product_url,
                        "title": title,
                        "price": price,
                        "real_price": real_price,
                        "rating": rating,
                        "prime_available": is_prime
                    })
                except Exception as e:
                    print(f"⚠️ Product parse error: {e}")

        await browser.close()

    if results:
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Saved {len(results)} results to {output}")
    else:
        print("❌ No data scraped.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default="shirts")
    parser.add_argument("--input", default="amazon_search.csv")
    parser.add_argument("--output", default="data/amazon_output.csv")
    parser.add_argument("--pages", type=int, default=3)
    args = parser.parse_args()
    asyncio.run(amazon_search_scraper(keyword=args.keyword, page_count=args.pages, output=args.output))
