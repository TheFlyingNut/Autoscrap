import asyncio
import pandas as pd
import os
from datetime import datetime
from playwright.async_api import async_playwright
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SEARCH_TERM = None
DATA_DIR = "static/data"
CSV_FILE = os.path.join(DATA_DIR, "flipkart_prices.csv")
HEADERS = ["Title", "Current Price", "Old Price", "Rating", "Reviews", "URL", "Last Seen", "Price Dropped?"]
SENDER_EMAIL = "youremail@gmail.com"
SENDER_PASS = "your_app_password"
RECEIVER_EMAIL = "youremail@gmail.com"

async def scroll_page(page, max_scrolls=3):
    print("[*] Scrolling the page to load more items...")
    for i in range(max_scrolls):
        await page.mouse.wheel(0, 4000)
        await page.wait_for_timeout(2500)
        print(f"[>] Scrolled {i+1}/{max_scrolls} times")

async def scrape_products(page):
    await page.goto(f"https://www.flipkart.com/search?q={SEARCH_TERM}")
    await page.wait_for_selector("div.DOjaWF div:nth-child(2)", timeout=15000)

    await scroll_page(page)

    containers = page.locator("div.DOjaWF div:nth-child(2) > div > div:has(div.KzDlHZ)")
    count = await containers.count()
    print(f"[+] Found {count} potential containers\n")

    products = []

    for i in range(count):
        box = containers.nth(i)
        print(f"\n--- Scraping container #{i+1} ---")

        title_el = box.locator("div.KzDlHZ")
        price_el = box.locator("div.Nx9bqj._4b5DiR")
        old_price_el = box.locator("div.yRaY8j ZYYwLA")
        rating_el = box.locator("div.XQDdHH")
        reviews_el = box.locator("span.Wphh3N")
        link_el = box.locator("a")

        try:
            if not await title_el.count():
                print("🔴 Title element not found.")
                continue

            title = await title_el.inner_text()
            print(f"🟢 Title: {title.strip()}")

            if not await price_el.count():
                print("🔴 Price element missing.")
                continue

            price_raw = await price_el.inner_text()
            price = int(price_raw.replace("₹", "").replace(",", ""))
            print(f"🟢 Current Price: ₹{price}")

            if await old_price_el.count():
                old_price_raw = await old_price_el.inner_text()
                old_price = int(old_price_raw.replace("₹", "").replace(",", ""))
                print(f"🟢 Old Price: ₹{old_price}")
            else:
                old_price = price
                print("🔵 Old price not found. Using current price.")

            rating = await rating_el.inner_text() if await rating_el.count() else "N/A"
            print(f"🟢 Rating: {rating.strip()}")

            reviews = await reviews_el.inner_text() if await reviews_el.count() else "0"
            print(f"🟢 Reviews: {reviews.strip()}")

            if not await link_el.count():
                print("🔴 Link not found.")
                continue

            href = await link_el.get_attribute("href")
            product_url = f"https://www.flipkart.com{href}"
            print(f"🟢 URL: {product_url}")

            product = {
                "Title": title.strip(),
                "Current Price": price,
                "Old Price": old_price,
                "Rating": rating.strip(),
                "Reviews": reviews.strip(),
                "URL": product_url,
                "Last Seen": datetime.now().strftime("%Y-%m-%d"),
                "Price Dropped?": "No"
            }

            products.append(product)

            if len(products) >= 50:
                break

        except Exception as e:
            print(f"❌ Error while scraping container {i+1}: {e}")

    print(f"\n[✓] Scraped total: {len(products)} valid products.")
    return products

def compare_with_old_data(new_data):
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(CSV_FILE):
        print("[*] No existing data found. Creating new file.")
        pd.DataFrame(new_data).to_csv(CSV_FILE, index=False)
        return

    old_df = pd.read_csv(CSV_FILE)
    old_df.set_index("URL", inplace=True)
    
    if int(product["Current Price"]) < old_price:
        product["Price Dropped?"] = "Yes"
        send_email_alert(product)

    for product in new_data:
        url = product["URL"]
        if url in old_df.index:
            old_price = int(old_df.loc[url, "Current Price"])
            if int(product["Current Price"]) < old_price:
                product["Price Dropped?"] = "Yes"
        else:
            product["Price Dropped?"] = "New"

    pd.DataFrame(new_data).to_csv(CSV_FILE, index=False)
    print("[✓] Updated and saved to CSV.")
    
def send_email_alert(product):
    subject = "🔔 Flipkart Price Drop Alert!"
    body = f"""
        🔥 <b>{product['Title']}</b><br>
        Old Price: ₹{product['Old Price']}<br>
        New Price: ₹{product['Current Price']}<br>
        Rating: {product['Rating']} ⭐<br>
        Reviews: {product['Reviews']}<br>
        <br>
        <a href="{product['URL']}">🔗 View Product</a>
    """

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASS)
            smtp.send_message(msg)
        print(f"[📧] Sent alert for: {product['Title'][:40]}...")
    except Exception as e:
        print(f"[❌] Failed to send email: {e}")
        
async def scrape_flipkart_with_keyword(keyword="laptop"):
    global SEARCH_TERM
    SEARCH_TERM = keyword
    await scrape_flipkart()

async def scrape_flipkart():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        print("[*] Browser launched. Starting scrape...\n")
        new_data = await scrape_products(page)
        await browser.close()
        compare_with_old_data(new_data)

if __name__ == "__main__":
    asyncio.run(scrape_flipkart())