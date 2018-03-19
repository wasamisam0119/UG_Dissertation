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

class DataFetcher(object):
       
    def __init__(self,name):
        self.f = open(name+"_extracted.json","r")
        if name =="sale":
            self.exf = open("sold.json","r")
        else:
            self.exf = open("rented.json","r")
        self.container = []
        self.pattern = re.compile("\w+")
        self.citypattern = re.compile("[A-Za-z]+")
        #self.read_configure("conf.txt")
        self.region_container={}

       # self.region_container= City(self.region)
       #for item in self.region:
         #   self.region_container[item] = []
    """
    def read_configure(self,con_file):
        with open(con_file,"r") as f:
            conf_list = list(map(myStrip,f.readlines()))
            self.region_list = conf_list[0].split(" ")  
              
            self.property_type = conf_list[1]
            self.bed = int(conf_list[2])
            self.startmonth= int(conf_list[3])
            self.endmonth = int(conf_list[4])
            self.usertype = conf_list[5]
            self.outputfile = conf_list[6]
            self.sorttype = conf_list[7] 
    """


    def extract_region(self, postcode):
        postcode_split = postcode.split()
        region  = self.pattern.search(postcode_split[1]).group(0)
        return region

    #return all the sold house information as a list of dicts
    def retrieve_sold_info(self):
        sold_house = []
        for item in self.f:
            # a big json contains all the extracted house info. file name:"sale_extracted.json"
            data = json.loads(item)
            for house in self.exf: # exf:"sold.json"
                ex_house = json.loads(house)
                #get the key(id) of the house
                house_id = next(iter(ex_house))
                if house_id in data:
                    origin_postcode = data[house_id]['postcode']
                    #get the region of the sold house
                    region = self.extract_region(origin_postcode)
                    data[house_id]["region"] = region
                    data[house_id]["super_region"] = self.citypattern.search(region).group(0)
                    data[house_id]["speed"] = self.calculate_salespeed(data[house_id]["first_published_date"],ex_house[house_id]["sold_time"])
                    data[house_id]["sold_date"] = timestamp_toDatetime(ex_house[house_id]["sold_time"])
                    sold_house.append(data[house_id])
        return sold_house

    def calculate_salespeed(self,published_date,sold_date):
        publish = string_toDatetime(published_date)
        sold = timestamp_toDatetime(sold_date)
        if publish ==-1 or sold == -1:
            return 0
        else:
            return (sold-publish).days

     

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


"""
        avg_ratio= {}

        for item in output_dict.items():
            for region in rentfilter.region_list:
                if rentfilter.citypattern.search(item[0]).group(0) ==region:
                    #fw.write(item[0]+" " +json.dumps(item[1],ensure_ascii=False)+"\n")
                    if "rent_ratio" in item[1]:
                        if region not in avg_ratio:
                            avg_ratio[region] = {}
                        if "ratio" not in avg_ratio[region]:
                            avg_ratio[region] = {}
                            avg_ratio[region]["ratio"] = item[1]["rent_ratio"]
                            avg_ratio[region]["l1"] = 1
                        else:
                            avg_ratio[region]["ratio"]+=item[1]["rent_ratio"]
                            avg_ratio[region]["l1"] += 1
        

        for item in output_dict.items():
            for region in rentfilter.region_list:
                if rentfilter.citypattern.search(item[0]).group(0) ==region:
                    if "sale_speed" in item[1]:
                        if "sale_speed" not in avg_ratio[region]:
                            avg_ratio[region]["sale_speed"] = item[1]["sale_speed"]
                            avg_ratio[region]["sale_median"]=item[1]["sale_median"]
                            avg_ratio[region]["sale_increase_rate"]=item[1]["sale_increase_rate"][11]
                            avg_ratio[region]["l"] = 1
                        else:
                            avg_ratio[region]["sale_speed"]+=item[1]["sale_speed"]
                            avg_ratio[region]["sale_median"]+=item[1]["sale_median"]
                            avg_ratio[region]["sale_increase_rate"]+=item[1]["sale_increase_rate"][11]
                            avg_ratio[region]["l"] += 1
                    if "rent_speed" in item[1]:
                        if "rent_speed" not in avg_ratio[region]:
                            avg_ratio[region]["rent_speed"] = item[1]["rent_speed"]
                            avg_ratio[region]["rent_median"]=item[1]["rent_median"]
                            avg_ratio[region]["rent_l"] = 1
                        else:
                            avg_ratio[region]["rent_speed"]+=item[1]["rent_speed"]
                            avg_ratio[region]["rent_median"]+=item[1]["rent_median"]
                            avg_ratio[region]["rent_l"] += 1


        for item in avg_ratio.items():
            avg_ratio[item[0]]["avg_sale_speed"] = round(item[1]["sale_speed"]/item[1]["l"],1)
            avg_ratio[item[0]]["avg_rent_speed"] = round(item[1]["rent_speed"]/item[1]["rent_l"],1)
            avg_ratio[item[0]]["avg_ratio"] = round(100/(item[1]["ratio"]/item[1]["l1"]),1)
            avg_ratio[item[0]]["avg_rent_price"] = round((item[1]["rent_median"]/item[1]["l1"]),1)
            avg_ratio[item[0]]["avg_sale_price"] = round((item[1]["sale_median"]/item[1]["l"]),1)
            avg_ratio[item[0]]["avg_increase_rate"] = round((item[1]["sale_increase_rate"]/item[1]["l"]),1)

        #output_json = json.dumps(output_dict,ensure_ascii=False)
        print(avg_ratio)
        import xlsxwriter
        workbook = xlsxwriter.Workbook("sale&rent_speed.xlsx")
        worksheet = workbook.add_worksheet()
        col = 0
        row = 0
        #worksheet.write(col,row,)
        for key, value in avg_ratio.items():
            worksheet.write(row,col,key)
            worksheet.write(row,col+1,value["avg_sale_speed"])
            worksheet.write(row,col+2,value["avg_rent_speed"])
            worksheet.write(row,col+3,value["avg_ratio"])
            worksheet.write(row,col+4,value["avg_rent_price"])
            worksheet.write(row,col+5,value["avg_sale_price"])
            worksheet.write(row,col+6,value["avg_increase_rate"])
            
            row+=1
        workbook.close()
    def calculate_city_avg(self,area_container, metrics,city_container):
        for item in area_container.items():
            for region in self.region_list:
                if self.citypattern.search(item[0]).group(0) ==region:
                    if metrics in item[1]:
                        if metrics not in avg_ratio[region]:
                            city_container[region][metrics] = item[1][metrics]
                            city_container[region]["l"] = 1
                        else:
                            avg_ratio[region][metrics]+=item[1][metrics]
                            avg_ratio[region]["l"] += 1
     
        print(avg_ratio)
        #fw.write("average rent_ratio is %f"%(avg_ratio/l))
        #fw.write(output_json)
        fw.close()
"""

s = DataFetcher("sale")
r = DataFetcher("rent")
s_df = pd.DataFrame(s.retrieve_sold_info())
r_df = pd.DataFrame(r.retrieve_sold_info())

#s_df.to_csv("sold_house.csv")
#r_df.to_csv("rent_house.csv")

#Filter.output('0',"output.txt",r,s)
#Filter.output('0',"%s_output.txt"%s.region,r,s)

        
"""
    def calculate_mid_price(self,key):
        price_list = []
        for item in self.region_container[key]:
            #print(item)
            price_list.append(item["price"])
        return median(price_list)

    def get_num_sales(self,key):
        return len(self.region_container[key])

    
    def get_midsale_speed(self,key):
        speed_list = []
        for item in self.region_container[key]:
            if item["speed"] != 0:
                speed_list.append(item["speed"])
        if len(speed_list) == 0:
            return -1
        return median(speed_list)

"""
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
 
