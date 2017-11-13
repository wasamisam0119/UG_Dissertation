# -*- coding: utf-8 -*-
import os
import json
import gc
#import re
import sys
import pytz
import time
import datetime
from spider.items import *


"""def format_add_time(originString):
    dateRegex = re.compile("\d{2}[a-z]+\s[a-z]+\s20\d{2}")
    if len(dateRegex.findall(originString))>0:
        formattedTime = dateRegex.findall(originString)[0]
    else:
        formattedTime = ""
    return formattedTime
"""

def myStrip(string):
    return string.strip()

def date_filter(datelist):
    for item in datelist:
        item = item.strip()
        format_add_time(item)
    filter_object  = filter((lambda x: x==""), datelist)
    datelist = [item for item in filter_object]
    return datelist


def trans_to_stamp(date):
    return time.mktime(time.strptime(date,'%Y-%m-%d %H:%M:%S'))

"""
class SoldPipeline(object):
    id_list = []
    def open_spider(self,spider):
        pass


    def close_spider(self,spider):
        #写到另一张表里去
        pass
"""

def set_timezone(timezone):
    tz = pytz.timezone(timezone)
    return datetime.datetime.now(tz).strftime("%d-%m-%Y")

class StorePipeline(object):
    sale_info =  'sale_house.json'
    rent_info = 'rent_house.json'
    ex_sale_name = 'sold.json'
    ex_rent_name = 'rented.json'
    house_rent_id ='house_rent_id.txt'
    house_sale_id = "house_sale_id.txt"
    all_rent_id = "all_rent_id.txt "
    all_sale_id = "all_sale_id.txt"
    timezone="Europe/London"
    sold_house_list = {}
    house_json_list = []
    id_list = []
    count =0
    start_time = time.time()
    
    # responsiable for adding new property/deleting sold property
    
    def activate_mode(self,mode,spider,property_info_file,current_id_file,all_id_file,ex_file):
        self.f = open(current_id_file,'a+')
        self.f.seek(0)
        temp_id_list = list(map(myStrip,self.f.readlines()))
        i = 0
        for item in temp_id_list:
            spider.house_id_dict[item] = i
            i+=1
        spider.house_id_list = temp_id_list
        if "zoopla" in spider.name:
            self.file = open(property_info_file, 'a') 
            self.wholeid_fp= open(all_id_file,'a+')
        else:
            #spider is soldSPider
            date = set_timezone(self.timezone)
            #create update file
            update_file = "../dailyupdate/%s_%s_update.json"%(mode,date)
            self.update_fp= open(update_file,"w+")
            #create solditem file
            self.file = open(ex_file,'a')

    def open_spider(self,spider):

        if "sale" in spider.name:
        #edit house.json
            self.activate_mode("sale",spider,self.sale_info,self.house_sale_id,self.all_sale_id,self.ex_sale_name)
        else:
            self.activate_mode("rent",spider,self.rent_info,self.house_rent_id,self.all_rent_id,self.ex_rent_name)

       
            
    def store_warehouse(self,mode,item, spider):
        if "zoopla" in spider.name:
            self.id_list.append(item['listing_id']+"\n")
            info_json = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.house_json_list.append(info_json)
            if len(self.id_list)==4:
                self.count+=4
                for i in range(len(self.id_list)):
                    #write id to house_id.txt
                    self.f.write(self.id_list[i])
                    #write id to house_id_whole.txt
                    self.wholeid_fp.write(self.id_list[i])
                    #write house info to house.json
                    self.file.write(self.house_json_list[i])
                self.id_list.clear()
                self.house_json_list.clear()
            if self.count%4000==0:
                gc.collect()
                self.count = 0
            if time.time() - self.start_time>10800:
                spider.close_down = True
                print("Time is up!!!!!")
            

        else:
            if isinstance(item,UpdateItem):
                #update house item
                update_json= json.dumps(dict(item), ensure_ascii=False) + '\n'
                self.update_fp.write(update_json)
            else:
                #SoldItem:{house_id:111111, sold_time:2017-02-03}
                #delete sold id
                del spider.house_id_dict[item['house_id']]
                #sold house item
                self.sold_house_list[item['house_id']]=dict(item)
                sold_house_info= json.dumps(self.sold_house_list, ensure_ascii=False) + '\n'
                self.file.write(sold_house_info)
                self.sold_house_list.clear()


    def process_item(self, item, spider):
        #不同的spider 进行不同的清洗和 append
        if "sale" in spider.name:
            self.store_warehouse("sale",item,spider)
        else:
            self.store_warehouse("rent",item,spider)
        return item

    def close_spider(self, spider):
        # close house.json or sold.json
        self.file.close()
        #close house_id.txt
        self.f.close()
        if "zoopla" in spider.name :
            self.wholeid_fp.close()
        else:
            self.update_fp.close()
            if len(spider.house_id_dict) >0 :
                if "salespider" in spider.name:
                    self.house_id_fp = open(self.house_sale_id,"w+")
                else:
                    self.house_id_fp = open(self.house_rent_id,"w+")
                for item in spider.house_id_dict:
                    self.house_id_fp.write(item+"\n")
                self.house_id_fp.close()
