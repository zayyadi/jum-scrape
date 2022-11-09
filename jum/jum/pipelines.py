# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy import Spider

from sqlalchemy.orm import sessionmaker

import dotenv

from jum.db import get_db, engine
from jum.items import JumItem
from jum.models import JumiaScrape

dotenv.load_dotenv()

logger = logging.getLogger(__name__)


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


class SavingToPostgresPipeline(object):
    def __init__(self):
        eng = engine
        self.Session = sessionmaker(bind=eng)

        self.prd = []

    # def create_connection(self):
    #     self.conn = psycopg2.connect(
    #         host="localhost",
    #         database="jumia_scraping",
    #         user="postgres",
    #         password=os.environ.get("DB_PASS"),
    #     )
    #     self.curr = self.conn.cursor()
    #     if self.curr:
    #         print(f"connected to Database: {self.curr}")

    def process_item(self, item: JumItem, spider: Spider) -> JumItem:

        product = dict(
            name=item["name"],
            price=item["price"],
            url=item["url"],
        )
        self.prd.append(product)
        return item

    # def store_db(self, item):
    #     try:
    #         self.curr.execute(
    #             """ insert into jumia_scrape values (%s,%s,%s)""",
    #             (),
    #         )
    #     except BaseException as e:
    #         print(e)
    #     self.conn.commit()

    def close_spider(self, spider: Spider) -> None:
        session = self.Session()

        try:
            logger.info("Saving products in bulk operation to the database.")
            session.bulk_insert_mappings(
                JumiaScrape, self.prd, return_defaults=True
            )  # Set `return_defaults=True` so that PK (inserted one at a time) value is available for FK usage at another table

            # logger.info("Saving prices in bulk operation to the database.")
            # prices = [
            #     dict(price=price, product_id=product["id"])
            #     for product, price in zip(self.products, self.prices)
            # ]
            # session.bulk_insert_mappings(Price, prices)
            session.commit()

        except Exception as error:
            logger.exception(error, extra=dict(spider=spider))
            session.rollback()
            raise

        finally:
            session.close()
