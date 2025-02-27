import scrapy


class GenericMedicineItem(scrapy.Item):
    drug_code = scrapy.Field()  # e.g., PMBJP item code
    name = scrapy.Field()  # e.g., "Metformin Hydrochloride Tablets IP 500mg"
    raw_composition = scrapy.Field()  # e.g., "Metformin Hydrochloride 500mg"
    dosage_form = scrapy.Field()  # e.g., "Tablet", "Capsule"
    pack_size = scrapy.Field()  # e.g., "10 Tablets"
    mrp = scrapy.Field()  # e.g., "7.50"
    category = scrapy.Field()  # e.g., "Anti-diabetic"
    source = scrapy.Field()  # e.g., "Jan Aushadhi (PMBJP)"


class BrandedMedicineItem(scrapy.Item):
    brand_name = scrapy.Field()  # e.g., "Glycomet 500 SR"
    manufacturer = scrapy.Field()  # e.g., "USV Ltd"
    raw_composition = scrapy.Field()  # e.g., "Metformin (500mg)"
    dosage_form = scrapy.Field()  # e.g., "Tablet"
    pack_size = scrapy.Field()  # e.g., "10 Tablets"
    mrp = scrapy.Field()  # e.g., "45.50"
    source = scrapy.Field()  # e.g., "Public Retail Catalog"