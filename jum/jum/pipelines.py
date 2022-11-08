# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from decimal import Decimal
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class JumPipeline:
    def process_item(self, item, spider):
        return item


class PriceConvPipeLine:
    ngn_usd = 1 / 800

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter.get("price"):

            decimalPrice = float(adapter["price"].replace(",", ""))
            adapter["price"] = decimalPrice * self.ngn_usd

            return item

        else:
            raise DropItem(f"missing Price in {item}")


class DuplicatesPipeline:
    def __init__(self):
        self.names_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if adapter["name"] in self.names_seen:
            raise DropItem(f"Duplicate Item found: {item}")

        else:
            self.names_seen.add(adapter["name"])
            return item
