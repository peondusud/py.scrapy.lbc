# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LeboncoinItem(scrapy.Item):
    doc_id = scrapy.Field()
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
