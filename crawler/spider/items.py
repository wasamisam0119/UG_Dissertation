# -*- coding: utf-8 -*-

import scrapy

class HouseEstDataItem(scrapy.Item):
    address = scrapy.Field()
    estimate_sell_price = scrapy.Field()
    estimate_rental_price = scrapy.Field()
    estimate_sell_range = scrapy.Field()
    estimate_rental_range = scrapy.Field()

class OnSaleHouseDataItem(scrapy.Item):

    #houseinfo
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
    first_published_date = scrapy.Field()
    house_id =scrapy.Field()
    category =scrapy.Field()
    country = scrapy.Field()
    county = scrapy.Field()
    details_url = scrapy.Field()
    displayable_address = scrapy.Field()
    last_published_date = scrapy.Field()
    latitude = scrapy.Field()
    listing_status = scrapy.Field()
    longitude = scrapy.Field()
    num_floors = scrapy.Field()
    num_recepts = scrapy.Field()
    outcode = scrapy.Field()
    post_town = scrapy.Field()
    property_report_url = scrapy.Field()
    property_type = scrapy.Field()
    status = scrapy.Field()
    floor_plan = scrapy.Field()

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
