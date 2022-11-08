from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst


class JumiaLoader(ItemLoader):

    default_output_processor = TakeFirst()
    price_in = MapCompose(lambda x: x.split("₦")[-1])
    url_in = MapCompose(lambda x: "https://jumia.com.ng/phones-tablets" + x)
