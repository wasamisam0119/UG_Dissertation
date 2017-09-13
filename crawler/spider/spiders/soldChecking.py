import scrapy
import spider.items
import json
import re
import requests
import time
import os
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import sys
sys.path.append("spiders")
from zoopla_on_sale_spider import transGBP
from zoopla_on_sale_spider import subDate

"""
This spider is used for checking the existing houses saved in local storage,
it will examine all the properties and record the sold items, update the other houses
"""

houseid_pattern = re.compile("\d+")

class OldChecking(scrapy.Spider):

    name = "soldspider"
    allowed_domains = ['zoopla.co.uk']
    start_urls = [
            'https://www.zoopla.co.uk/for-sale/']

    #init the house id dict
    house_id_dict={}

    #all the property id will be read into the dict when open the spider--see ../pipelines.py def open_spider() 
    def parse(self, response):
        for n in self.house_id_dict:
            yield response.follow("/for-sale/details/"+n, callback=self.parse_house)

    def parse_house(self, response):

        title = response.css("h2.listing-details-h1::text").extract_first()
        #if already sold
        if not title:
            #mark as sold
            sold_house = spider.items.SoldItem()
            sold_house['house_id'] = houseid_pattern.search(response.request.meta.get('redirect_urls')[0]).group()
            sold_house['sold_time'] = time.mktime(time.localtime())
            return sold_house

        else:
            update_item = spider.items.UpdateItem()
            listing_id  = response.css("html").re('listing_id":"(.*?)"')[0]
            update_item['house_id'] = listing_id

            crawling_time = time.strftime("%d-%m-%Y", time.localtime())
            update_item['crawling_time'] = crawling_time

            month_view= response.xpath("//*[@id=\"listings-agent\"]/div[4]/p[2]/strong[2]/text()").extract_first()
            if month_view!=None:
                update_item['month_view'] = int(month_view.replace(",",""))
            else:
                update_item['month_view'] = -1

            #update price change since listed
            asking_price_change = []
            for each in response.css("ul.most_reduced_list li::text").extract():
                if each.strip()!="":
                    asking_price_change.append(transGBP(each.strip())) 

            #format 1st July 2015
            price_change_date = response.css("span.date::text").re("(?:Increased|Reduced) on:\s*(.*)")
            if len(asking_price_change)>0:
                #here subDate method is to substitude English date format 
                #into standard date format
                price_change_date = map(subDate,price_change_date)
                update_item['price_change'] = list(zip(asking_price_change,price_change_date))
            return update_item
 
