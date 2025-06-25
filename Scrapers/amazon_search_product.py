import asyncio
from playwright.async_api import async_playwright
import csv

async def scrape_amazon_products(input_file='static/data/amazon_search.csv', output_file = 'static/data/amazon_product_output.csv'):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        with open(input_file, 'r') as f:
            reader = csv.DictReader(f)
            urls = [row['url'] for row in reader]

        results = []
        for url in urls:
            print(f"🌐 Scraping: {url}")
            try:
                await page.goto(url, timeout=60000)
                
                # Name (required field)
                name = await page.locator("#title").text_content() if await page.locator("#title").count() else "N/A"
                
                # Price (multiple fallbacks)
                price = None
                for selector in [
                    "#corePriceDisplay_desktop_feature_div span.a-price-whole",
                    ".a-price-whole",
                    ".a-offscreen"
                ]:
                    if await page.locator(selector).count():
                        price = await page.locator(selector).first.text_content()
                        break
                
                # Sizes (optional)
                sizes = []
                if await page.locator("#tp-inline-twister-dim-values-container ul").count():
                    sizes = await page.locator("#tp-inline-twister-dim-values-container ul").all_inner_texts()
                
                # Ratings (with multiple fallbacks)
                stars = "N/A"
               
                # Try main rating container first
                if await page.locator("#averageCustomerReviews").count():
                    stars = await page.locator("#averageCustomerReviews i span").text_content() if await page.locator("#averageCustomerReviews i span").count() else "N/A"
                else:
                    if await page.locator("span[data-hook=rating-out-of-text]").count():
                        stars = await page.locator("span[data-hook=rating-out-of-text]").text_content()
                
                ratings_count = "N/A"
                for count_selector in [
                    "#acrCustomerReviewText",  # Your specified selector
                    "span[data-hook=total-review-count]",
                    "#averageCustomerReviews span#acrCustomerReviewText",
                    "div[data-hook=total-review-count]",
                    "#reviewsMedley .a-size-base"
                ]:
                    if await page.locator(count_selector).count():
                        ratings_count = (await page.locator(count_selector).first.text_content()).strip()
                        break

                results.append({
                    "name": name.strip(),
                    "price": price.strip() if price else "N/A",
                    "sizes": "|".join(sizes) if sizes else "N/A",
                    "stars": stars.strip(),
                    "ratings_count": ratings_count.strip()
                })
                print(f"✅ Success: {name[:30]}...")

            except Exception as e:
                print(f"❌ Failed {url}: {str(e)[:100]}...")
                continue

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        await browser.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="amazon_search.csv")
    parser.add_argument("--output", default="data/amazon_product_output.csv")
    args = parser.parse_args()
    asyncio.run(scrape_amazon_products(input_file = args.input, output_file = args.output))