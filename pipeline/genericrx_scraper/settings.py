BOT_NAME = "genericrx_scraper"

SPIDER_MODULES = ["pipeline.genericrx_scraper.spiders"]
NEWSPIDER_MODULE = "pipeline.genericrx_scraper.spiders"

# Crawl responsibly by respecting standard browser headers
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Obey robots.txt rules where applicable
ROBOTSTXT_OBEY = False

# Configure concurrency and delay to avoid hitting rate limits
CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 1.0

# Encoding
FEED_EXPORT_ENCODING = "utf-8"

# Reactor configuration
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"