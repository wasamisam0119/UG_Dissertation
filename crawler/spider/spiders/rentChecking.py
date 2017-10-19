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

houseid_pattern = re.compile("\d+")
class RentChecking(scrapy.Spider):

    name = "rentspider"
    allowed_domains = ['zoopla.co.uk']
    start_urls = [
            'https://www.zoopla.co.uk/to-rent/']

    house_id_dict={}

    def parse(self, response):
        print("number of the id_dict is %s"%len(self.house_id_dict))
        for n in self.house_id_dict.keys():
            yield response.follow("/to-rent/details/"+n, callback=self.parse_house)
        print("yield all the links!")

    def parse_house(self, response):

        title = response.css("h2.listing-details-h1::text").extract_first()
        if not title:
            print(response.request.meta.get('redirect_urls'))
            sold_house = spider.items.SoldItem()
            sold_house['house_id'] = houseid_pattern.search(response.request.meta.get('redirect_urls')[0]).group()
            sold_house['sold_time'] = time.mktime(time.localtime())
            #mark as sold
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

            asking_price_change = []
                        #price change since listed
            for each in response.css("ul.most_reduced_list li::text").extract():
                if each.strip()!="":
                    if "pcm" in each:
                        asking_price_change.append(transGBP(each.strip()[:-4])) 

        #format 1st July 2015
        #may need change to standard time
            price_change_date = response.css("span.date::text").re("(?:Increased|Reduced) on:\s*(.*)")
            if len(asking_price_change)>0:
                price_change_date = map(subDate,price_change_date)
                update_item['price_change'] = list(zip(asking_price_change,price_change_date))
            return update_item
 
