import json
from statistics import median
import re
from datetime import datetime

def myStrip(string):
    return string.strip()
def string_toDatetime(string):
    if string ==-1:
        return -1 
    else:
        return datetime.strptime(string, "%d-%m-%Y")

def timestamp_toDatetime(timestamp):
    return datetime.fromtimestamp(timestamp)

class Filter(object):
    """
    region
    date
    timegap
    property_type
    
    """

    
    def __init__(self,name):
        self.f = open(name+"_extracted.json","r")
        if name =="sale":
            self.exf = open("sold.json","r")
        else:
            self.exf = open("rented.json","r")
        self.container = []
        self.pattern = re.compile("\w+")
        self.citypattern = re.compile("[A-Za-z]+")
        self.read_configure("conf.txt")
        self.region_container={}

       # self.region_container= City(self.region)
       #for item in self.region:
         #   self.region_container[item] = []
    def read_configure(self,con_file):
        with open(con_file,"r") as f:
            conf_list = list(map(myStrip,f.readlines()))
            self.region =conf_list[0]  
            self.property_type = conf_list[1]
            self.bed = int(conf_list[2])
            self.startmonth= int(conf_list[3])
            self.endmonth = int(conf_list[4])
            self.usertype = conf_list[5]
            self.outputfile = conf_list[6]


    def extract_region(self, postcode):
        postcode_split = postcode.split()
        region  = self.pattern.search(postcode_split[1]).group(0)
        return region

    def start_filter(self):
        
        #house_id = 0
        for item in self.f:
            # a big json contains all the extracted house info. file name:"sale_extracted.json"
            self.data = json.loads(item)
            for house in self.exf: # exf:"sold.json"
                ex_house = json.loads(house)
                #get the key(id) of the house
                house_id = next(iter(ex_house))
                if house_id in self.data:
                    origin_postcode = self.data[house_id]['postcode']
                    #get the region of the sold house
                    region = self.extract_region(origin_postcode)
                    if self.region == self.citypattern.search(region).group(0):
                        #print(type(self.data[house_id]['num_bed']))
                        if self.bed ==self.data[house_id]['num_bed']:
                            if self.property_type == self.data[house_id]['property_type']:
                                print(self.data[house_id]['postcode'])
                                if self.region_container.get(region) is None:
                                    self.region_container[region] = []
                                    self.data[house_id]["speed"] = self.calculate_salespeed(self.data[house_id]["first_published_date"],ex_house[house_id]["sold_time"])
                                    self.data[house_id]["sold_date"] = timestamp_toDatetime(ex_house[house_id]["sold_time"])
                                    self.region_container[region].append(self.data[house_id])
                                else:
                                    self.data[house_id]["speed"] = self.calculate_salespeed(self.data[house_id]["first_published_date"],ex_house[house_id]["sold_time"])
                                    self.region_container[region].append(self.data[house_id])
                                    self.data[house_id]["sold_date"] = timestamp_toDatetime(ex_house[house_id]["sold_time"])


    def MoM_increase_rate(self,key, house_type="default"):
        
        self.monthly_container = {}
        month_increase_dict = {}

        for item in self.region_container[key]:
            month = item["sold_date"].month
            if self.startmonth<= month <= self.endmonth:
                if month not in self.monthly_container:
                    self.monthly_container[month] = {}
                    self.monthly_container[month]["price"] = [] 
                    self.monthly_container[month]["price"].append(item["price"]) 
                else:
                    self.monthly_container[month]["price"].append(item["price"]) 
        for item in self.monthly_container:
            self.monthly_container[item]["median"] = median(self.monthly_container[item]["price"])


        for x in range(self.startmonth+1,self.endmonth+1):
            if x in self.monthly_container and x-1 in self.monthly_container :
                month_increase_dict[x] = self.monthly_increase(self.monthly_container[x]["median"],self.monthly_container[x-1]["median"]) 
            else:
                month_increase_dict[x] = 0.0
        return month_increase_dict

                    
    def monthly_increase(self,x1,x2):
        return round(100*(x1-x2)/x2,2)


                    

    def calculate_mid_price(self,key):
        price_list = []
        for item in self.region_container[key]:
            #print(item)
            price_list.append(item["price"])
        return median(price_list)

    def get_num_sales(self,key):
        return len(self.region_container[key])

    def calculate_salespeed(self,published_date,sold_date):
        publish = string_toDatetime(published_date)
        sold = timestamp_toDatetime(sold_date)
        if publish ==-1 or sold == -1:
            return 0
        else:
            return (sold-publish).days


    @staticmethod
    def calculate_rent_ratio(avg_rent,avg_sale):
        return round(100*(avg_rent/avg_sale),2)

    def get_midsale_speed(self,key):
        speed_list = []
        for item in self.region_container[key]:
            if item["speed"] != 0:
                speed_list.append(item["speed"])
        return median(speed_list)

    @staticmethod
    def output(usertype,filename,rentfilter,salefilter):
        fw = open(filename,"w")
        output_dict = {}
        tem_dict = []
        if usertype == '0':
            for key,value in salefilter.region_container.items():

                output_dict[key] ={}
                if key in rentfilter.region_container:
                    output_dict[key]["rent_median"] =rentfilter.calculate_mid_price(key) 
                    output_dict[key]["rent_num_sales"] = rentfilter.get_num_sales(key)
                    output_dict[key]["rent_speed"] =rentfilter.get_midsale_speed(key)

                output_dict[key]["sale_median"] =salefilter.calculate_mid_price(key) 
                output_dict[key]["sale_num_sales"] =salefilter.get_num_sales(key)
                output_dict[key]["sale_speed"] =salefilter.get_midsale_speed(key)
                output_dict[key]["sale_increase_rate"] = salefilter.MoM_increase_rate(key)
            for key,value in rentfilter.region_container.items():
                if key not in output_dict:
                    output_dict[key] = {}
                if key in salefilter.region_container:
                    output_dict[key]["sale_median"] =salefilter.calculate_mid_price(key) 
                    output_dict[key]["sale_num_sales"] =salefilter.get_num_sales(key)
                    output_dict[key]["sale_speed"] =salefilter.get_midsale_speed(key)

                output_dict[key]["rent_median"] =rentfilter.calculate_mid_price(key) 
                output_dict[key]["rent_num_sales"] = rentfilter.get_num_sales(key)
                output_dict[key]["rent_speed"] =rentfilter.get_midsale_speed(key)
                output_dict[key]["rent_increase_rate"] = rentfilter.MoM_increase_rate(key)

            for key,value in output_dict.items():
                if 'rent_median' in value and 'sale_median' in value:
                    output_dict[key]["rent_ratio"] =Filter.calculate_rent_ratio(value["rent_median"],value["sale_median"]) 
        else:
            pass
        
        for item in output_dict.items():
            fw.write(item[0]+" " +json.dumps(item[1],ensure_ascii=False)+"\n")
        #output_json = json.dumps(output_dict,ensure_ascii=False)
        #fw.write(output_json)
        fw.close()


s = Filter("sale")
r = Filter("rent")
r.start_filter()
s.start_filter()
Filter.output('0',"output.txt",r,s)


        
class City(object):
    def __init__(self,name):
        self.name = name
        self.subRegion = []
        
class Subregion(City):
    pass

"""
self.region =[ 
"AB",
"AL",
"B",
"BA",
"BB",
"BD",
"BH",
"BL",
"BN",
"BR",
"BS",
"BT",
"CA",
"CB",
"CF",
"CH",
"CM",
"CO",
"CR",
"CT",
"CV",
"CW",
"DA",
"DD",
"DE",
"DG",
"DH",
"DL",
"DN",
"DT",
"DY",
"E",
"EC",
"EH",
"EN",
"EX",
"FK",
"FY",
"G",
"GL",
"GU",
"HA",
"HD",
"HG",
"HP",
"HR",
"HS",
"HU",
"HX",
"IG",
"IP",
"IV",
"KA",
"KT",
"KW",
"KY",
"L",
"LA",
"LD",
"LE",
"LL",
"LN",
"LS",
"LU",
"M",
"ME",
"MK",
"ML",
"N",
"NE",
"NG",
"NN",
"NP",
"NR",
"NW",
"OL",
"OX",
"PA",
"PE",
"PH",
"PL",
"PO",
"PR",
"RG",
"RH",
"RM",
"S",
"SA",
"SE",
"SG",
"SK",
"SL",
"SM",
"SN",
"SO",
"SP",
"SR",
"SS",
"ST",
"SW",
"SY",
"TA",
"TD",
"TF",
"TN",
"TQ",
"TR",
"TS",
"TW",
"UB",
"W",
"WA",
"WC",
"WD",
"WF",
"WN",
"WR",
"WS",
"WV",
"YO",
"ZE"]
        """
 
