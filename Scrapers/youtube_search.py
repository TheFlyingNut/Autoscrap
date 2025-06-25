import asyncio
from playwright.async_api import async_playwright
import csv

async def scrape_youtube_search(keyword="Python Tutorial", target_count=50, output_file="youtube_results.csv"):
    url = "https://www.youtube.com"
    video_data = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  
        page = await browser.new_page()
        await page.goto(url, timeout=60000)

        try:
            await page.locator("button:has-text('Accept all')").click(timeout=5000)
        except:
            pass

        await page.wait_for_selector('//*[@id="center"]/yt-searchbox/div[1]/form/input', timeout=15000)
        await page.fill('//*[@id="center"]/yt-searchbox/div[1]/form/input', keyword)
        await page.press('//*[@id="center"]/yt-searchbox/div[1]/form/input', "Enter")

        await page.wait_for_selector("ytd-video-renderer", timeout=15000)

        previous_count = 0
        scroll_delay = 2000
        max_scrolls = 50

        for _ in range(max_scrolls):
            await page.mouse.wheel(0, 5000)
            await page.wait_for_timeout(scroll_delay)

            videos = await page.locator("ytd-video-renderer").all()
            current_count = len(videos)

            if current_count >= target_count:
                break

            if current_count == previous_count:
                scroll_delay += 1000
            previous_count = current_count

        videos = await page.locator("ytd-video-renderer").all()
        for v in videos[:target_count]:
            try:
                title = await v.locator("#video-title").get_attribute("title")
                url = await v.locator("#video-title").get_attribute("href")
                channel = await v.locator("ytd-channel-name").first.inner_text()
                meta = await v.locator("#metadata-line span").all_inner_texts()
                views = meta[0] if len(meta) > 0 else "N/A"
                upload = meta[1] if len(meta) > 1 else "N/A"

                video_data.append({
                    "title": title.strip() if title else "N/A",
                    "channel": channel.strip(),
                    "views": views.strip(),
                    "upload_date": upload.strip(),
                    "url": f"https://www.youtube.com{url}" if url else "N/A"
                })
            except:
                continue

        await browser.close()

    if video_data:
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=video_data[0].keys())
            writer.writeheader()
            writer.writerows(video_data)

    return video_data  # so Flask can use it too

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--keyword", default="Python Tutorial")
    parser.add_argument("--count", type=int, default=50)
    parser.add_argument("--output", default="data/youtube_results.csv")
    args = parser.parse_args()

    asyncio.run(scrape_youtube_search(args.keyword, args.count, args.output))
