import scrapy
import spider.items
import json

path = "../../zoopla_on_sale.json"

class OnSaleHouseSpider(scrapy.Spider):
    name = "zoopla_on_sale"

    filename = "zoopla_on_sale.json"

    """Get the latest house info stored in local file"""
    """will be used to compared with online house info to implement realtime crawling"""
    def get_house_list():
        f = open(path,"a+")
        local_newest_house = json.loads(f.readline())
        return (local_newest_house['added_time'],local_newest_house['price'])

    local_house_info = get_house_list()

    start_urls = [
            'http://www.zoopla.co.uk/for-sale/property/england/?q=England&results_sort=newest_listings&search_source=for-sale'
    ]


    def parse(self, response):
        for house_url in response.css("div.listing-results-wrapper a.listing-results-price.text-price::attr(href)").extract():
            yield response.follow(house_url, callback=self.parse_house)

        next_page_url = response.css("div.paginate.bg-muted a:last-child::attr(href)").extract_first()
        yield response.follow(next_page_url, callback=self.parse)

    def parse_house(self, response):

        title = response.css("h2.listing-details-h1::text").extract_first()

        price = response.css("div.listing-details-price.text-price strong::text").extract_first().strip()

        street_address = response.css("div.listing-details-address h2::text").extract_first()

        num_of_bedrooms = response.css("span.num-icon.num-beds::text").extract_first()

        num_of_bathrooms = response.css("span.num-icon.num-baths::text").extract_first()

        num_of_receptions = response.css("span.num-icon.num-reception::text").extract_first()
        
        added_time =response. response.xpath("//*[@id=\"listings-agent\"]/div[4]/p[1]/text()").extract()

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
        house_data_item['added_time'] = added_time
        
        return house_data_item
