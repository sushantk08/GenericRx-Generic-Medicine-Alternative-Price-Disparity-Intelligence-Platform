import json
import scrapy
from pipeline.genericrx_scraper.items import BrandedMedicineItem


class BrandedMedicineSpider(scrapy.Spider):
    name = "branded_medicines"
    allowed_domains = ["netmeds.com", "medplusmart.com"]

    start_urls = [
        "https://www.netmeds.com/brand/netmeds?categorynamelevel2=Antidiabetic+Agents&departments=medicine",
        "https://www.medplusmart.com/drugsInfo/medicines/medicines_10001/vitamins_30103",
    ]

    custom_settings = {
        "DOWNLOAD_DELAY": 2.0,
        "ROBOTSTXT_OBEY": False,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    }

    def parse(self, response):
        """Extract product cards and medicine information from Netmeds and Medplusmart."""

        # 1. Attempt to parse embedded Schema.org JSON-LD (reliable structured metadata)
        json_ld_scripts = response.xpath(
            '//script[@type="application/ld+json"]/text()'
        ).getall()
        found_json_items = False

        for raw_json in json_ld_scripts:
            try:
                data = json.loads(raw_json)
                items_list = []
                if isinstance(data, dict):
                    if data.get("@type") == "Product":
                        items_list = [data]
                    elif "itemListElement" in data:
                        items_list = [
                            entry.get("item", {})
                            for entry in data["itemListElement"]
                            if isinstance(entry, dict)
                        ]
                elif isinstance(data, list):
                    items_list = [
                        d
                        for d in data
                        if isinstance(d, dict) and d.get("@type") == "Product"
                    ]

                for p in items_list:
                    if p.get("name"):
                        item = BrandedMedicineItem()
                        item["brand_name"] = p.get("name", "").strip()
                        item["manufacturer"] = (
                            p.get("brand", {}).get("name", "Unknown")
                            if isinstance(p.get("brand"), dict)
                            else str(p.get("brand", "Unknown"))
                        )
                        item["raw_composition"] = p.get(
                            "description", item["brand_name"]
                        ).strip()
                        item["pack_size"] = "10 Tablets"
                        offers = p.get("offers", {})
                        item["mrp"] = str(
                            offers.get("price", "0")
                            if isinstance(offers, dict)
                            else "0"
                        )
                        item["dosage_form"] = (
                            "Tablet"
                            if "tab" in item["brand_name"].lower()
                            else (
                                "Capsule"
                                if "cap" in item["brand_name"].lower()
                                else "Other"
                            )
                        )
                        item["source"] = response.url
                        found_json_items = True
                        yield item
            except json.JSONDecodeError:
                continue

        # 2. HTML DOM Parsing for Netmeds and Medplusmart cards
        # Netmeds uses .cat-item, .drug-list, .ais-InfiniteHits-item
        # Medplus uses .product-card, .drug-info, or table rows
        cards = response.css(
            ".cat-item, .drug-list, .product-card, .ais-InfiniteHits-item, div[class*='productCard'], div[class*='product_item']"
        )

        if not cards:
            cards = response.xpath(
                "//div[contains(@class, 'product') or contains(@class, 'item') or contains(@class, 'card')]"
            )

        for card in cards:
            # Netmeds specific selectors
            name = (
                card.css(".clsgetname::text").get()
                or card.css("h3::text").get()
                or card.css("h2::text").get()
                or card.xpath(
                    ".//span[contains(@class, 'name') or contains(@class, 'title')]/text()"
                ).get()
            )

            composition = (
                card.css(".drug-varients::text").get()
                or card.css(".drug-varients-sub::text").get()
                or card.xpath(
                    ".//span[contains(@class, 'composition') or contains(@class, 'salt')]/text()"
                ).get()
                or card.xpath(
                    ".//div[contains(@class, 'variant') or contains(@class, 'desc')]/text()"
                ).get()
            )

            mrp = (
                card.css("#final_price::text").get()
                or card.css(".final-price::text").get()
                or card.xpath(
                    ".//span[contains(@class, 'price') or contains(@class, 'mrp')]/text()"
                ).get()
            )

            manufacturer = (
                card.css(".drug-manu::text").get()
                or card.xpath(
                    ".//span[contains(@class, 'manufacturer') or contains(@class, 'brand')]/text()"
                ).get()
            )

            pack_size = card.css(".drug-unit::text").get() or card.xpath(
                ".//span[contains(@class, 'pack') or contains(@class, 'unit')]/text()"
            ).get()

            if name and (mrp or composition):
                item = BrandedMedicineItem()
                item["brand_name"] = name.strip()
                item["raw_composition"] = (
                    composition.strip() if composition else name.strip()
                )
                item["manufacturer"] = (
                    manufacturer.strip() if manufacturer else "Unknown"
                )
                item["pack_size"] = (
                    pack_size.strip() if pack_size else "10 Tablets"
                )
                item["mrp"] = (
                    mrp.replace("₹", "").replace("Rs.", "").strip()
                    if mrp
                    else "0"
                )
                item["dosage_form"] = (
                    "Tablet"
                    if "tab" in name.lower()
                    else ("Capsule" if "cap" in name.lower() else "Other")
                )
                item["source"] = response.url
                yield item

        # 3. Follow pagination
        next_page = response.xpath(
            "//a[contains(@class, 'next') or contains(text(), 'Next') or contains(@rel, 'next')]/@href"
        ).get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)