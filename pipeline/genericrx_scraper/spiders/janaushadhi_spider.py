import scrapy
from pipeline.genericrx_scraper.items import GenericMedicineItem


class JanAushadhiSpider(scrapy.Spider):
    name = "janaushadhi"
    allowed_domains = ["janaushadhi.gov.in"]

    # Public catalog URL for PMBJP product listings
    start_urls = [
        "https://janaushadhi.gov.in/ProductList.aspx",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 1.5,
        "ROBOTSTXT_OBEY": False,
    }

    def parse(self, response):
        """Parse tabular product listings from the catalog page."""
        # Locate table rows in the catalog listing
        rows = response.xpath("//table[contains(@id, 'GridView')]//tr[position() > 1]")

        if not rows:
            # Fallback selector for alternative table layouts
            rows = response.xpath("//table//tr[td]")

        for row in rows:
            cols = row.xpath("./td/text()").getall()
            cols = [c.strip() for c in cols if c.strip()]

            # Expected columns typically: [Code, Generic Name, Composition, Packing, MRP]
            if len(cols) >= 5:
                item = GenericMedicineItem()
                item["drug_code"] = cols[0]
                item["name"] = cols[1]
                item["raw_composition"] = cols[2]
                item["pack_size"] = cols[3]
                item["mrp"] = cols[4].replace("Rs.", "").replace("₹", "").strip()
                item["category"] = cols[5] if len(cols) > 5 else "General"
                item["source"] = "Jan Aushadhi (PMBJP)"

                yield item

        # Handle pagination if 'Next' page link exists
        next_page = response.xpath(
            "//a[contains(text(), 'Next') or contains(@title, 'Next')]/@href"
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)