import scrapy
import spider.items
import json
import re
import requests
import time
import os
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class OldChecking(scrapy.Spider):

    name = "soldspider"
    filename = "zoopla_on_sale.json"
    allowed_domains = ['zoopla.co.uk']
    start_urls = [
            'https://www.zoopla.co.uk/for-sale/']

    def read_house_id(file_name):
        fp = open(file_name,"r+")
        list_of_lines = fp.readlines()
        return list_of_lines

    def get_house_list():
        f = open(path,"a+")
        local_newest_house = json.loads(f.readline())
        return (local_newest_house['first_published_date'],local_newest_house['price'])

    house_id_list = read_house_id()
#    house_id_list = read_house_id(file_id)
#    house_id_set = set(house_id_list)
    #house_id_dict = dict(zip(house_id_list,[x for x in range(len(house_id_list))]))
    #print(house_id_dict)
    house_list = []

    def parse(self, response,house_id_list):
        for n in house_id_list:
            yield response.follow("for-sale/details/"+n, callback=self.parse_house)

    def parse_house(self, response):

        title = response.css("h2.listing-details-h1::text").extract_first()
        if not title:
            sold_house = spider.items.SoldItem()
            sold_house['house_id'] = houseid_pattern.search(response.url).group()
            sold_house['sold_time'] = time.mktime(time.localtime())
            #mark as sold
            return sold_house
        price = transGBP(response.css("div.listing-details-price.text-price strong::text").extract_first().strip())

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
            asking_price_change.append(each) 
        #???
        #需要判断是否存在
        total_views = response.xpath("//*[@id=\"listings-agent\"]/div[4]/p[2]/strong[2]").extract()

        energy_cost = response.css("button[data-rc-name = Energy]::attr(data-rc-value)").extract_first()
        insurance_cost = response.css("button[data-rc-name = Insurance]::attr(data-rc-value)").extract_first() 
        council_tax = response.css("button[data-rc-name=Council\ Tax]::attr(data-rc-value)").extract_first() 
        water_cost = response.css("button[data-rc-name = Water]::attr(data-rc-value)").extract_first() 

        #sale nearby
        #return a list of top3 date
        top3date= response.css("td.neither--top span.date::text").extract()

        #return a list of top3 postcode
        #format sn1-2cn
        top3postcode = response.css("td.neither--top a::attr(href)").re('[a-z]+[0-9]+-\w+')
        
        #return a list of top3 price
        top3price = response.css("td.neither--top.right strong::text").extract()
        top3price = map(transGBP,top3price)

        #format [(a,b,c),(d,e,f)]
        top3sale_near_by = list(zip(top3date,top3price,top3postcode))

        #todo 
        #get the status change time

        #rebuild_value = response.css("span.rc-details-panel-item-quote::text").extract_first()
        #content_value = response.css("span.rc-details-panel-item-quote::text").extract_first()

        #print(response.url)
        #print(rebuild)
        #print(insurance_cost)
        price_change_date = []
        for each in response.css("span.date::text").extract():
            price_change_date.append(each) 


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
        #house_info
        house_data_item = spider.items.OnSaleHouseDataItem()
        house_data_item['title'] = title
        house_data_item['price'] = price
        house_data_item['street_address'] = street_address
        house_data_item['num_of_bedrooms'] = num_of_bedrooms
        house_data_item['num_of_bathrooms'] = num_of_bathrooms

        house_data_item['num_of_receptions'] = num_of_receptions

        house_data_item['images'] = images

        house_data_item['property_features'] = property_features

        house_data_item['property_description'] = property_description
        
        house_data_item['transport_information'] = transport_information
        #call the api and return a json dict
        house_api_json = get_API_info(response.url)
        house_data_item['first_published_date'] = house_api_json['listing'][0]['first_published_date']
        house_data_item['latitude'] = house_api_json['listing'][0]['latitude']
        house_data_item['house_id'] = house_api_json['listing'][0]['listing_id']
        house_data_item['category'] = house_api_json['listing'][0]['category']
        house_data_item['country'] = house_api_json['listing'][0]['country']
        house_data_item['county'] = house_api_json['listing'][0]['county']
        house_data_item['details_url'] = house_api_json['listing'][0]['details_url']
        house_data_item['displayable_address'] = house_api_json['listing'][0]['displayable_address']
        house_data_item['last_published_date'] = house_api_json['listing'][0]['last_published_date']
        house_data_item['latitude'] = house_api_json['listing'][0]['latitude']
        house_data_item['listing_status'] = house_api_json['listing'][0]['listing_status']
        house_data_item['longitude'] = house_api_json['listing'][0]['longitude']
        house_data_item['num_floors'] = house_api_json['listing'][0]['num_floors']
        house_data_item['num_recepts'] = house_api_json['listing'][0]['num_recepts']
        house_data_item['outcode'] = house_api_json['listing'][0]['outcode']
        house_data_item['post_town'] = house_api_json['listing'][0]['post_town']
        house_data_item['property_report_url'] = house_api_json['listing'][0]['property_report_url']
        house_data_item['property_type'] = house_api_json['listing'][0]['property_type']
        house_data_item['status'] = house_api_json['listing'][0]['status']
        if 'floor_plan' in house_api_json['listing'][0]:
            house_data_item['floor_plan'] = house_api_json['listing'][0]['floor_plan']
        #agent info
        house_data_item['agent_address'] = house_api_json['listing'][0]['agent_address']
        house_data_item['agent_name'] = house_api_json['listing'][0]['agent_name']
        house_data_item['agent_phone'] = house_api_json['listing'][0]['agent_phone']
        #price change
        house_data_item['price_change'] = []
        if len(house_api_json['listing'][0]['price_change'])>1:
            house_data_item['price_change'] = house_api_json['listing'][0]['price_change'][1:]



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
        house_data_item['top3near_by'] = top3sale_near_by

        return house_data_item
