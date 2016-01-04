# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.org/en/1.0/topics/items.html
#http://doc.org/en/1.0/topics/loaders.html

from scrapy.item import Item, Field
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
    doc_id = Field(
        #input_processor= TakeFirst()
        #output_processor= Join()
        )
    doc_url = Field()
    doc_category = Field()
    title = Field()
    img_urls = Field()
    thumbs_urls = Field()
    user_url = Field()
    user_id = Field()
    user_name = Field()
    user_pro = Field()
    user_pro_siren = Field()
    upload_date = Field()
    check_date = Field()

    price_currency = Field()
    price = Field()
    urgent = Field()

    region = Field()
    addr_locality = Field()
    postal_code = Field()
    location = Field()

    criterias = Field()

    desc = Field()
