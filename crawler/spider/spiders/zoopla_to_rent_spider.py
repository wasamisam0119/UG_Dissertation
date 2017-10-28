import scrapy
import spider.items
import json
import re
import requests
import datetime
import time
import os
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import sys
sys.path.append("spiders")
from zoopla_on_sale_spider import transGBP
from zoopla_on_sale_spider import subDate
from scrapy.exceptions import CloseSpider

def myStrip(string):
    return string.strip()

class ToRentHouseSpider(CrawlSpider):
    name = "zoopla_to_rent"
    filename = "zoopla_to_rent.json"
    allowed_domains = ['zoopla.co.uk']
    house_id_dict = {}
    close_down = False
    start_urls = [
            'https://www.zoopla.co.uk/to-rent/']
    rules = (
        Rule(LinkExtractor(allow=('/to-rent/browse/.*',),),),
        Rule(LinkExtractor(allow=('/to-rent/property/.*/',),),),
        Rule(LinkExtractor(allow=('/to-rent/details/',),),
             callback="parse_house"),
    )

    def parse_house(self, response):

        if self.close_down:
            raise CloseSpider(reason='Usage exceeded')
        listing_id  = response.css("html").re('listing_id":"(.*?)"')[0]
        if listing_id in self.house_id_dict:
            print("Find duplicate item and Drop! Drop id is %s"%listing_id)
            return
        else:
            self.house_id_dict[listing_id] = len(self.house_id_dict)
            title = response.css("h2.listing-details-h1::text").extract_first()
            rent_price = response.css("div.listing-details-price.text-price strong::text").extract_first().strip()

            street_address = response.css("div.listing-details-address h2::text").extract_first()

            num_of_bedrooms = response.css("span.num-icon.num-beds::text").extract_first()

            num_of_bathrooms = response.css("span.num-icon.num-baths::text").extract_first()

            num_of_receptions = response.css("span.num-icon.num-reception::text").extract_first()
            
            #list_history
            """
            if len(response.css(".sbt p.top::text").extract())>=2:
                    first_list_price = transGBP(response.css(".sbt p.top::text").extract()[1].strip())
                    """
            asking_price_change = []
            #price change since listed
            for each in response.css("ul.most_reduced_list li::text").extract():
                if each.strip()!="":
                    if "pcm" in each.strip():
                        asking_price_change.append(transGBP(each.strip()[:-4])) 


            #format 1st July 2015
            #may need change to standard time
            price_change_date = response.css("span.date::text").re("(?:Increased|Reduced) on:\s*(.*)")

            #需要判断是否存在
            crawling_time = time.strftime("%d-%m-%Y", time.localtime())
            month_view= response.xpath("//*[@id=\"listings-agent\"]/div[4]/p[2]/strong[2]/text()").extract_first()
            
            energy_cost = response.css("button[data-rc-name = Energy]::attr(data-rc-value)").extract_first()
            insurance_cost = response.css("button[data-rc-name = Insurance]::attr(data-rc-value)").extract_first() 
            council_tax = response.css("button[data-rc-name=Council\ Tax]::attr(data-rc-value)").extract_first() 
            water_cost = response.css("button[data-rc-name = Water]::attr(data-rc-value)").extract_first() 

                    #todo 
            #get the status change time

            #rebuild_value = response.css("span.rc-details-panel-item-quote::text").extract_first()
            #content_value = response.css("span.rc-details-panel-item-quote::text").extract_first()

            # images
            images = []
            for url in response.css("a.images-thumb::attr(data-photo)").extract():
                images.append(url)

            # property_features
            property_features = [] 
            for each in response.css("#tab-details div.clearfix li::text").extract():
                property_features.append(each)

            # property_description
            property_description = ""
            for each in response.css("div.bottom-plus-half *.top::text").extract():
                property_description += each
            property_description = property_description.strip()

            
            # transport_information 
            transport_information = []
            for each in response.css("span.area-reports--item__name"):
                station_name = each.css("::attr(title)").extract_first()
                distance = each.css("span.area-reports--item__distance::text").extract_first().strip("()")
                transport_information.append({station_name:distance})

            agent_address = response.css("span[itemprop=address] span[itemprop=streetAddress]::text").extract()
            agent_name =response.css("strong[itemprop=name] a[itemprop=url]::text").extract() 
            agent_phone = response.css("span.agent_phone a[itemprop=telephone]::text").extract()
            

            #house_info
            house_data_item = spider.items.OnRentHouseDataItem()
            house_data_item['title'] = title
            if "pcm" in rent_price:
                house_data_item['monthly_price'] = transGBP(rent_price[:-4])
            else:
                house_data_item['monthly_price'] = transGBP(rent_price)

            price_type = response.css("span.price-modifier::text").extract_first()
            if price_type!=None:
                house_data_item['price_type'] = price_type
            else:
                house_data_item['price_type'] = "normal"
                
            house_data_item['crawling_time'] = crawling_time
            house_data_item['street_address'] = street_address
            if len(asking_price_change)>0:
                price_change_date = map(subDate,price_change_date)
                house_data_item['price_change'] = list(zip(asking_price_change,price_change_date))
            if num_of_bedrooms!=None:
                house_data_item['num_of_bedrooms'] = int(num_of_bedrooms)
            else:
                house_data_item['num_of_bedrooms'] = -1
            if num_of_bathrooms!=None:
                house_data_item['num_of_bathrooms'] = int(num_of_bathrooms)
            else:
                house_data_item['num_of_bathrooms'] = -1
            if month_view!=None:
                house_data_item['month_view'] =int(month_view)
            else:
                house_data_item['month_view'] =-1

            if len(agent_address)>0:
                house_data_item['agent_address'] = agent_address[0]
            else:
                house_data_item['agent_address'] = ""
            
            if len(agent_name)>0:
                house_data_item['agent_name'] = agent_name[0]
            else:
                house_data_item['agent_name'] = ""

            if len(agent_phone)>0:
                house_data_item['agent_phone'] =agent_phone[0]
            else:
                house_data_item['agent_phone'] =""

            first_published_date = response.css("div.sidebar.sbt p.top::text").re("on\s*(.*)")
            if len(first_published_date)>0:
                first_published_date = subDate(first_published_date[0])
                house_data_item['first_published_date'] = first_published_date

            #sale nearby
            #return a list of top3 date
            top3date= response.css("td.neither--top span.date::text").extract()
            
            top3date = list(map(subDate,map(myStrip,top3date)))

            #return a list of top3 postcode
            #format sn1-2cn
            top3postcode = response.css("td.neither--top a::attr(href)").re('[a-z]+[0-9]+-\w+')
            #return a list of top3 price
            top3price = response.css("td.neither--top.right strong::text").extract()
            top3price = map(transGBP,top3price)
            
            #format [(a,b,c),(d,e,f)]
            top3sale_near_by = list(zip(top3date,top3price,top3postcode))
            house_data_item['top3near_by'] = top3sale_near_by

            house_data_item['num_of_receptions'] = num_of_receptions

            house_data_item['images'] = images

            house_data_item['property_features'] = property_features

            house_data_item['property_description'] = property_description
            
            house_data_item['transport_information'] = transport_information
            #call the api and return a json dict

            if response.css("img.floorplan-img::attr(src)").extract_first():
                house_data_item['floor_plan'] = response.css("img.floorplan-img::attr(src)").extract_first()
            else:
                house_data_item['floor_plan'] = ""

            incode = response.css("html").re('incode":"(.*?)"')[0]
            outcode = response.css("html").re('outcode":"(.*?)"')[0]
            house_data_item['listing_id'] = listing_id
            house_data_item['postcode'] = incode+" "+ outcode

            house_data_item['coordinate'] = (
                    response.css("html").re('lat = (.*),')[0],
                    response.css("html").re('lon = (.*);')[0])

            #house cost
            if  water_cost != None:
                house_data_item['water_cost'] =  int(water_cost)
            else:
                house_data_item['water_cost'] = -1

            if council_tax!= None:
                house_data_item['council_tax'] = int(council_tax)
            else:
                house_data_item['council_tax'] = -1

            if insurance_cost != None:
                house_data_item['insurance_cost'] = int(insurance_cost)
            else:
                house_data_item['insurance_cost'] = -1

            if energy_cost !=None:
                house_data_item['energy_cost'] = int(energy_cost)
            else:
                house_data_item['energy_cost'] = -1

            #top3 house

            return house_data_item
