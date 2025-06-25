from apscheduler.schedulers.blocking import BlockingScheduler
import asyncio
import logging
from Scrapers.flipkart_scraper import scrape_flipkart  # make sure function is exposed

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', hour=10, minute=0)
def scheduled_task():
    print("Running daily Flipkart scrape...")
    try:
        asyncio.run(scrape_flipkart())
        print("Flipkart scraping done.")
    except Exception as e:
        print(f"Error during scheduled scrape: {e}")

if __name__ == "__main__":
    print("Scheduler started. Press Ctrl+C to exit.")
    scheduler.start()