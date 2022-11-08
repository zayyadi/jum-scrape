import scrapy
from jum.items import JumItem
from jum.itemloader import JumiaLoader


class JumiaSpider(scrapy.Spider):
    name = "jumia"
    allowed_domains = ["jumia.com.ng"]
    start_urls = ["https://jumia.com.ng/phones-tablets"]

    def parse(self, response):
        # products get data from parent div from which we are to loop from other variable
        products = response.css("div.itm.col")

        for product in products:
            jumia = JumiaLoader(item=JumItem(), selector=product)
            jumia.add_css("name", "div.name::text"),
            jumia.add_css("price", "div.prc::text"),
            jumia.add_css("url", "a.core::attr(href)"),
            yield jumia.load_item()

        # for next page
        """
        next_page = response.css('[rel="next"] ::attr(href)').get()

        if next_page is not None:
            next_page_url = 'https://www.chocolate.co.uk' + next_page
            yield response.follow(next_page_url, callback=self.parse)
         """
