# -*- coding: utf-8 -*-
import os
import json
#import re
import sys
import pytz
import time
import datetime
from spider.items import *

#import pymysql

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
    # responsiable for adding new property/deleting sold property
    
    def activateMode(mode,spidername,property_info_file,current_id_file,all_id_file,ex_file):
        if "zoopla" in spidername:
            f = open(current_id_file,'a+')
            f.seek(0)
            temp_id_list = list(map(myStrip,self.f.readlines()))
            i = 0
            for item in temp_id_list:
                spider.house_id_dict[item] = i
                i+=1
            self.file = open(property_info_file, 'a') 
            self.wholeid_fp= open(all_id_file,'a+')
        else:
            #spider is soldSPider
            date = set_timezone(self.timezone)
            #create update file
            update_file = "../dailyupdate/%s_%s_update.json"%(mode,date)
            self.update_fp= open(update_file,"w+")
            #create solditem file
            self.file = open(self.ex_file,'a')
 
    def open_spider(self,spider):

        if "sale" in spider.name:
        #edit house.json
            activateMode("sale",spider.name,sale_info,house_sale_id,all_sale_id,ex_sale_name)
        else:
            activateMode("rent",spider.name,rent_info,house_rent_id,all_rent_id,ex_rent_name)

       
            
    def process_item(self, item, spider):
        #不同的spider 进行不同的清洗和 append
        if spider.name =="zoopla_on_sale":
            self.id_list.append(item['listing_id']+"\n")

            house_json = json.dumps(dict(item), ensure_ascii=False) + '\n'
            
            self.house_json_list.append(house_json)
            if len(self.id_list)==256:
                for i in range(len(self.id_list)):
                    #write id to house_id.txt
                    self.f.write(self.id_list[i])
                    #write id to house_id_whole.txt
                    self.wholeid_fp.write(self.id_list[i])
                    #write house info to house.json
                    self.file.write(self.house_json_list[i])
                self.id_list.clear()
                self.house_json_list.clear()
"""
        elif spider.name =="zoopla_to_rent":
            if 
            """


        else:

            if isinstance(item,SoldItem):
                #SoldItem:{house_id:111111, sold_time:2017-02-03}
                #delete sold id
                del spider.house_id_dict[item['house_id']]
                #sold house item
                self.sold_house_list[item['house_id']]=dict(item)
                sold_house_info= json.dumps(self.sold_house_list, ensure_ascii=False) + '\n'
                self.file.write(sold_house_info)
                self.sold_house_list.clear()
            else:
                #update house item
                update_json= json.dumps(dict(item), ensure_ascii=False) + '\n'
                self.update_fp.write(update_json)

        # this means if the crawler now traverse to the house that match the
        # same house in local storage, stop the crawler

        return item
    def close_spider(self, spider):
        # close house.json or sold.json
        self.file.close()
        #close house_id.txt
        self.f.close()
        if spider.name == "zoopla_on_sale":
            self.wholeid_fp.close()
        else:
            self.update_fp.close()
            if len(spider.house_id_dict) >0 :
                self.house_id_fp = open("house_id.txt","w+")
                for item in spider.house_id_dict:
                    self.house_id_fp.write(item+"\n")
                self.house_id_fp.close()
            #1.写入不同的数据表
