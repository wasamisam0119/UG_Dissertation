# -*- coding: utf-8 -*-

import scrapy

class SoldItem(scrapy.Item):
    house_id = scrapy.Field() 
    sold_time = scrapy.Field()

class OnSaleHouseDataItem(scrapy.Item):

    #houseinfo
    crawling_time =scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    price_type = scrapy.Field()
    street_address = scrapy.Field()
    num_of_bedrooms = scrapy.Field()
    num_of_bathrooms = scrapy.Field()
    num_of_receptions = scrapy.Field()
    images = scrapy.Field()
    property_features = scrapy.Field()
    property_description = scrapy.Field()
    transport_information = scrapy.Field()
    added_time = scrapy.Field()
    first_published_date = scrapy.Field()
    listing_id=scrapy.Field()
    monthview=scrapy.Field()
    category = scrapy.Field()
    country = scrapy.Field()
    county = scrapy.Field()
    details_url = scrapy.Field()
    displayable_address = scrapy.Field()
    last_published_date = scrapy.Field()
    listing_status = scrapy.Field()
    coordinate=scrapy.Field()
    num_floors = scrapy.Field()
    num_recepts = scrapy.Field()
    outcode = scrapy.Field()
    postcode= scrapy.Field()
    property_report_url = scrapy.Field()
    property_type = scrapy.Field()
    floor_plan = scrapy.Field()

#    price change in history
    price_change =scrapy.Field() 
    #Monthly cost
    energy_cost= scrapy.Field()
    insurance_cost = scrapy.Field()
    council_tax = scrapy.Field()
    water_cost = scrapy.Field()

    
    #agency infomation 
    agent_address = scrapy.Field()
    agent_name = scrapy.Field()
    agent_phone = scrapy.Field()

    #top 3 sale house
    top3near_by = scrapy.Field()

    sold_time = scrapy.Field()
