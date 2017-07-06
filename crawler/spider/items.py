# -*- coding: utf-8 -*-

import scrapy

class HouseEstDataItem(scrapy.Item):
    address = scrapy.Field()
    estimate_sell_price = scrapy.Field()
    estimate_rental_price = scrapy.Field()
    estimate_sell_range = scrapy.Field()
    estimate_rental_range = scrapy.Field()

class OnSaleHouseDataItem(scrapy.Item):

    title = scrapy.Field()
    price = scrapy.Field()
    street_address = scrapy.Field()
    num_of_bedrooms = scrapy.Field()
    num_of_bathrooms = scrapy.Field()
    num_of_receptions = scrapy.Field()
    images = scrapy.Field()
    property_features = scrapy.Field()
    property_description = scrapy.Field()
    transport_information = scrapy.Field()
    added_time = scrapy.Field()


    
