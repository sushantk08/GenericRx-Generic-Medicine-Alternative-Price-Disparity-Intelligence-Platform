from datetime import datetime, timezone
import json
from pathlib import Path
from itemadapter import ItemAdapter


class RawJsonExportPipeline:
    """Streams scraped items into raw JSON files partitioned by spider name."""

    def open_spider(self, spider):
        # Resolve path to data/raw directory
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