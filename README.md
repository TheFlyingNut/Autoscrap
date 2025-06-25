AutoScrap 🧰

A Production-Ready Web Scraping Dashboard

AutoScrap is a centralized scraping framework built using Flask, Playwright, Scrapy, Pandas, and Bootstrap, designed to collect, visualize, and track data from platforms like Reddit, YouTube, Amazon, and Flipkart. It offers a clean UI, persistent tracking with CSV, price drop alerts via email, and automation support.

📄 Features

✨ Beautiful Flask-based UI with card-style navigation and glowing hover effects

⏰ Scheduler and loader support for Flipkart price tracking

⚖️ Reddit post scraper with subreddit targeting & visualizations

🎩 YouTube search result scraper (title, views, upload, etc.)

🛎️ Amazon search scraper and product detail scraper

📈 Flipkart tracker with price drop alerts, review count, CSV versioning

🔄 Chained Amazon scraping (search -> product scrape)

🚀 Email alert integration via Gmail SMTP

💡 Tools & Frameworks


Web Scraping:

Playwright, Scrapy, XPath Selectors

Backend:

Flask, Python asyncio, routing

Frontend:

HTML, CSS, JS, Jinja, Bootstrap-like styling

Storage:

Pandas, CSV-based history tracking

Scheduler:

Windows Task Scheduler, scheduler.py

Visualization:

Chart.js (for dynamic bar charts)

Alert System:

smtplib + Gmail SMTP

🧲 How It Works

1. Scrapers

Each scraper is modular:

Reddit: Scrapes latest N posts from a subreddit via Playwright

YouTube: Gets metadata from top search results

Amazon: Uses chained scraping (search -> scrape each product)

Flipkart: Scrapes 50+ products, checks historical CSV, and alerts on price drops

2. Centralized Control (Flask)

app.py contains all Flask routes

Each scraper has its own page (Jinja templates)

Loader shows during scraping

Visualizations powered by JavaScript + Chart.js

All input is sanitized and handled via forms

3. Data Output

All results are stored inside /Scrapers/data/*.csv

Products are tracked over time and compared

CSV is available to download

4. Email Alerts

Flipkart sends email if price drops > previous saved value

Configured via Gmail app password in flipkart_tracker.py

5. Scheduler (Optional)

Use scheduler.py to run Flipkart tracker daily (Windows compatible).

🚀 Getting Started

1. Clone the Repo

git clone https://github.com/yourusername/AutoScrap.git
cd AutoScrap

2. Install Requirements

pip install -r requirements.txt

3. Setup Gmail for Flipkart Alerts (Optional)

Enable 2FA in Gmail

Generate an App Password

Paste it in flipkart_tracker.py:

SENDER_EMAIL = "youremail@gmail.com"
SENDER_PASS = "your_app_password"
RECEIVER_EMAIL = "youremail@gmail.com"

4. Run the Flask Dashboard

python app.py

Navigate to: http://127.0.0.1:5000

5. Schedule Flipkart Tracking (Optional)

Open Task Scheduler (Windows)

Set to run scheduler.py daily

📁 Project Structure

AutoScrap/
├── app.py                    
├── scheduler.py             
├── Scrapers/                
│   ├── amazon_search.py
│   ├── amazon_search_product.py
│   ├── youtube_search.py
│   ├── redditscraper.py
│   └── flipkart_tracker.py
├── templates/
│   ├── index.html
│   ├── reddit.html
│   ├── amazon.html
│   ├── youtube.html
│   └── flipkart.html
├── static/
    ├── data/
    ├── styles/
      └── styles.css


python-dotenv

Also run: playwright install after installing requirements

🎉 Credits

Built with sleepless nights, Red Bulls, and aggressive debugging by Kartik 🤝 ChatGPT (aka his spider brother).

🚨 Disclaimer

This project is for educational purposes. Always respect the robots.txt and terms of service of the target websites.

Happy Scraping! 🚀
