# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/1.0/topics/items.html
#http://doc.scrapy.org/en/1.0/topics/loaders.html

from scrapy import Item
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join


class LeboncoinLoader(ItemLoader):
    default_input_processor = TakeFirst()
    default_output_processor = TakeFirst()

    title_in = MapCompose(unicode.title)
    title_out = Join()

    price_in = MapCompose(unicode.strip)
    price_out =  Join()


class LeboncoinItem(Item):
    doc_id = scrapy.Field(
        input_processor=
        output_processor=Join()
        )
    doc_url = scrapy.Field()
    doc_category = scrapy.Field()
    title = scrapy.Field()
    img_urls = scrapy.Field()
    user_url = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_pro = scrapy.Field()
    user_pro_siren = scrapy.Field()
    upload_date = scrapy.Field()

    price_currency = scrapy.Field()
    price = scrapy.Field()
    urgent = scrapy.Field()

    region = scrapy.Field()
    addr_locality = scrapy.Field()
    postal_code = scrapy.Field()
    location = scrapy.Field()

    criterias = scrapy.Field()

    desc = scrapy.Field()
