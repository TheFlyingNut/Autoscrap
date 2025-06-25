from flask import Flask, render_template, request, redirect, url_for, send_file
import asyncio
import os

# Import scraper functions from your Scrapers folder
from Scrapers.youtube_search import scrape_youtube_search
from Scrapers.redditscraper import scrape_reddit
from Scrapers.amazon_search import amazon_search_scraper
from Scrapers.amazon_search_product import scrape_amazon_products
from Scrapers.flipkart_scraper import scrape_flipkart_with_keyword

app = Flask(__name__)

# ---------- ROUTES ----------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/reddit')
def reddit_page():
    return render_template('reddit.html')

@app.route('/youtube')
def youtube_page():
    return render_template('youtube.html')

@app.route('/amazon')
def amazon_page():
    return render_template('amazon.html')

@app.route('/flipkart')
def flipkart_page():
    return render_template('flipkart.html')

# ---------- SCRAPER RUN ROUTES ----------

@app.route('/run/reddit', methods=['POST'])
def run_reddit():
    subreddit = request.form.get("subreddit", "Python")
    count = int(request.form.get("count", 50))
    output = "static/data/reddit_results.csv"
    asyncio.run(scrape_reddit(subreddit=subreddit, target_count=count, output_csv=output))
    return redirect(url_for('reddit_page'))

@app.route('/run/youtube', methods=['POST'])
def run_youtube():
    keyword = request.form.get("keyword", "Python Tutorial")
    count = int(request.form.get("count", 50))
    output = "static/data/youtube_results.csv"
    asyncio.run(scrape_youtube_search(keyword, count, output))
    return redirect(url_for('youtube_page'))

@app.route('/run/amazon', methods=['POST'])
def run_amazon():
    keyword = request.form.get("keyword", "shirts")
    pages_str = request.form.get("pages")
    pages = int(pages_str) if pages_str and pages_str.strip().isdigit() else 2
    search_output = "static/data/amazon_search.csv"
    detail_output = "static/data/amazon_product_details.csv"
    
    # Run both search and product detail scraping
    asyncio.run(amazon_search_scraper(keyword=keyword, page_count=pages, output=search_output))
    asyncio.run(scrape_amazon_products(input_file=search_output, output_file=detail_output))

    return redirect(url_for('amazon_page'))

@app.route('/run/flipkart', methods=['POST'])
def run_flipkart():
    keyword = request.form.get("keyword", "laptop")
    schedule = request.form.get("schedule")
    asyncio.run(scrape_flipkart_with_keyword(keyword))
    return redirect(url_for('flipkart_page'))

# ---------- DOWNLOAD ROUTES ----------

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join('static', 'data', filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    app.run(debug=True)
