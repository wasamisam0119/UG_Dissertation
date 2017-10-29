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
from scrapy.exceptions import CloseSpider

path = "../../zoopla_on_sale.json"
houseid_pattern = re.compile("\d+")
house_id = ""
apikey = "cmhxwgjs5qggn2uv7yh8qvv2"
file_id = "test.txt"


def get_API_info(house_url):
            houseid_ob = houseid_pattern.search(house_url)
            house_id = houseid_ob.group()
            api_url = "http://api.zoopla.co.uk/api/v1/property_listings.json?listing_id=%s&api_key=%s"%(house_id,apikey)
            js = json.loads(requests.get(api_url).text)
            return js
            #return js['listing'][0]['first_published_date']

def myStrip(string):
    return string.strip()

def transGBP(pounds):
    if len(pounds) == 0:
        return
    else:
        if pounds[0] == '£':
            return int(pounds[1:].replace(",", ""))
        else:
            return int(pounds.replace(",", ""))

def subDate(date):
    date = re.sub("st|th|nd|rd","",date)
    d = datetime.datetime.strptime(date,"%d %b %Y")
    date= datetime.datetime.strftime(d,"%d-%m-%Y")
    return date 


class OnSaleHouseSpider(CrawlSpider):
    name = "zoopla_on_sale"
    filename = "zoopla_on_sale.json"
    allowed_domains = ['zoopla.co.uk']
    house_id_dict = {}
    start_urls = [
            'https://www.zoopla.co.uk/for-sale/']
    rules = (
        Rule(LinkExtractor(allow=('/for-sale/browse/.*',),),),
        Rule(LinkExtractor(allow=('/for-sale/property/.*/',),),),
        Rule(LinkExtractor(allow=('/for-sale/details/',),),
             callback="parse_house"),
    )
    close_down = False


    """Get the latest house info stored in local file"""
    """will be used to compared with online house info to implement realtime crawling"""

    def get_house_list():
        f = open(path,"a+")
        local_newest_house = json.loads(f.readline())
        return (local_newest_house['first_published_date'],local_newest_house['price'])

    """
    def parse(self, response,house_id_list):
        for n in house_id_list:
            yield response.follow("for-sale/details/"+n, callback=self.parse_house)
        for house_url in response.css("div.listing-results-wrapper a.listing-results-price.text-price::attr(href)").extract():
            #print(house_url)
            yield response.follow(house_url, callback=self.parse_house)

        next_page_url = response.css("div.paginate.bg-muted a:last-child::attr(href)").extract_first()

        yield response.follow(next_page_url, callback=self.parse)
    
"""
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
                if each.strip()!="":
                    asking_price_change.append(transGBP(each.strip())) 

            #format 1st July 2015
            #may need change to standard time
            price_change_date = response.css("span.date::text").re("(?:Increased|Reduced) on:\s*(.*)")



            #???
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
            house_data_item = spider.items.OnSaleHouseDataItem()
            house_data_item['title'] = title
            house_data_item['price'] = price
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
                house_data_item['month_view'] =int(month_view.replace(",",""))
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
            house_data_item['postcode'] = incode+" "+outcode

            house_data_item['coordinate'] = (
                    response.css("html").re('lat = (.*),')[0],
                    response.css("html").re('lon = (.*);')[0])


            '''
            house_api_json = get_API_info(response.url)
            house_data_item['first_published_date'] = house_api_json['listing'][0]['first_published_date']
            1house_data_item['latitude'] = house_api_json['listing'][0]['latitude']
            1house_data_item['house_id'] = house_api_json['listing'][0]['listing_id']
            1house_data_item['category'] = house_api_json['listing'][0]['category']
            1house_data_item['country'] = house_api_json['listing'][0]['country']
            1house_data_item['county'] = house_api_json['listing'][0]['county']
            1house_data_item['details_url'] = house_api_json['listing'][0]['details_url']
            1house_data_item['displayable_address'] = house_api_json['listing'][0]['displayable_address']
            1house_data_item['last_published_date'] = house_api_json['listing'][0]['last_published_date']
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
                '''



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
