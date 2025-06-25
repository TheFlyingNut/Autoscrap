import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import csv
import math
import re

async def scrape_reddit(subreddit="Python", timeframe="all", sort="top", target_count=50, output_csv="reddit_posts.csv"):
    url = f"https://www.reddit.com/r/{subreddit}/{sort}/?t={timeframe}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_timeout(5000)

        max_scrolls = 40
        previous_count = 0
        html = ""

        for i in range(max_scrolls):
            await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2500)

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            current_count = len(soup.find_all("shreddit-post"))

            print(f"🌀 Scroll {i + 1}: {current_count} posts loaded")

            if current_count >= target_count:
                print("✅ Enough posts loaded.")
                break

            if current_count == previous_count:
                print("⚠️ No new posts loaded. Breaking.")
                break

            previous_count = current_count

        await browser.close()

    posts = soup.find_all("shreddit-post")
    data = []

    for post in posts:
        if len(data) >= target_count:
            break
        try:
            title = post.get("post-title") or post.find("a", {"id": re.compile("post-title")}).text.strip()
            author = post.get("author") or "N/A"
            upvotes = post.get("score") or "0"
            comments = post.get("comment-count") or "0"

            time_tag = post.find("faceplate-timeago")
            time_val = time_tag.find("time")["datetime"] if time_tag and time_tag.find("time") else "N/A"

            link = post.get("permalink") or post.find("a", href=True)["href"]
            full_link = "https://www.reddit.com" + link if link else "N/A"

            data.append({
                "title": title,
                "author": author,
                "upvotes": upvotes,
                "comments": comments,
                "url": full_link,
                "time": time_val
            })
        except Exception as e:
            print("⚠️ Parse error:", e)

    with open(output_csv, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"✅ Saved {len(data)} posts to {output_csv}")
    return output_csv

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddit", default="Python")
    parser.add_argument("--sort", default="top")
    parser.add_argument("--time", default="all")
    parser.add_argument("--posts", type=int, default=50)
    parser.add_argument("--output", default="data/reddit_posts.csv")
    args = parser.parse_args()

    asyncio.run(scrape_reddit(
        subreddit=args.subreddit,
        timeframe=args.time,
        sort=args.sort,
        target_count=args.posts,
        output_csv=args.output
    ))
