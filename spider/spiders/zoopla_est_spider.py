import scrapy
import spider.items


class HouseEstSpider(scrapy.Spider):
    name = "zoopla_est"

    start_urls = [
            "http://www.zoopla.co.uk/house-prices/browse/england/?q=England"
    ]

    def parse(self, response):
        for city_url in response.css("td.browse-cell-first a::attr(href)").extract():
            yield response.follow(city_url, callback=self.parse_city)

    def parse_city(self, response):
        for town_url in response.css("td.browse-cell-first a::attr(href)").extract():
            yield response.follow(town_url, callback=self.parse_town)

    def parse_town(self, response):
        for table_row_selector in response.css("tr.row-even,tr.row-odd"):
            est_price = table_row_selector.css("td:last-child::text").extract_first()
            if est_price == "—":
                continue
            street_url = response.css("a.sold-prices-results-address::attr(href)").extract_first()
            yield response.follow(street_url, callback=self.parse_street)

    def parse_street(self, response):
        for table_row_selector in response.css("tr.row-even,tr.row-odd"):
            est_price = table_row_selector.css("span.browse-estimate-value>a>span::text").extract_first().strip()
            if est_price == "Not known" or est_price == "":
                continue
            address_url = table_row_selector.css("td.browse-cell-address a:first-child::attr(href)").extract_first()

            yield response.follow(address_url, callback=self.parse_address)

    def parse_address(self, response):
        address = response.css("h1.neither::text").extract_first()[21:]
        estimate_sell_price = response.css("strong.big.zestimate::text").extract_first()
        estimate_rental_price = response.css("li.estimate-col-3 strong.big span.big::text").extract_first()
        estimate_sell_range = response.css("li.estimate-col-2>strong::text").extract_first()
        estimate_rental_range = response.css("li.estimate-col-3>strong::text").extract_first()
        estimate_data_item = spider.items.HouseEstDataItem()
        estimate_data_item['address'] = address
        estimate_data_item['estimate_sell_price'] = estimate_sell_price
        estimate_data_item['estimate_rental_price'] = estimate_rental_price
        estimate_data_item['estimate_sell_range'] = estimate_sell_range
        estimate_data_item['estimate_rental_range'] = estimate_rental_range
        return estimate_data_item
