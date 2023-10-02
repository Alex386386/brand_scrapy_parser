import json
import os


class ProductInfoPipeline:
    def __init__(self):
        self.data = {}
        self.output_file_path = 'maksavit_parser/output/products.json'

    def process_item(self, item, spider):
        category = item['section'][1]

        if category not in self.data:
            self.data[category] = []

        self.data[category].append(dict(item))

        return item

    def close_spider(self, spider):
        directory = os.path.dirname(self.output_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(self.output_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
