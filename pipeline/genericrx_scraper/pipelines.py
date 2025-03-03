from datetime import datetime, timezone
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from itemadapter import ItemAdapter
from pymongo import MongoClient

load_dotenv()


class RawJsonExportPipeline:
    """Streams scraped items into raw JSON files partitioned by spider name."""

    def open_spider(self, spider):
        project_root = Path(__file__).resolve().parents[2]
        self.output_dir = project_root / "data" / "raw"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.file_path = self.output_dir / f"{spider.name}_raw.json"
        self.file = open(self.file_path, "w", encoding="utf-8")
        self.file.write("[\n")
        self.first_item = True

    def close_spider(self, spider):
        self.file.write("\n]\n")
        self.file.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        item_dict = adapter.asdict()
        item_dict["scraped_at"] = datetime.now(timezone.utc).isoformat()

        line = json.dumps(item_dict, ensure_ascii=False, indent=2)

        if not self.first_item:
            self.file.write(",\n")
        else:
            self.first_item = False

        self.file.write(line)
        return item


class MongoStorePipeline:
    """Stores raw scraped item documents into MongoDB collections."""

    def __init__(self):
        user = os.getenv("MONGO_USER", "genericrx")
        password = os.getenv("MONGO_PASSWORD", "")
        host = os.getenv("MONGO_HOST", "localhost")
        port = os.getenv("MONGO_PORT", "27018")
        db_name = os.getenv("MONGO_DB", "genericrx_raw")

        self.mongo_uri = (
            f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"
        )
        self.db_name = db_name
        self.client = None
        self.db = None
        self.collection = None

    def open_spider(self, spider):
        try:
            self.client = MongoClient(
                self.mongo_uri, serverSelectionTimeoutMS=3000
            )
            self.db = self.client[self.db_name]
            self.collection = self.db[f"{spider.name}_raw"]
            spider.logger.info(
                f"Connected to MongoDB: storing in collection '{spider.name}_raw'"
            )
        except Exception as e:
            spider.logger.error(f"Failed to connect to MongoDB pipeline: {e}")
            self.client = None

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        if self.client is not None and self.collection is not None:
            adapter = ItemAdapter(item)
            item_dict = adapter.asdict()
            item_dict["ingested_at"] = datetime.now(timezone.utc).isoformat()
            try:
                self.collection.insert_one(item_dict)
            except Exception as e:
                spider.logger.warning(
                    f"Could not insert document to MongoDB: {e}"
                )
        return item