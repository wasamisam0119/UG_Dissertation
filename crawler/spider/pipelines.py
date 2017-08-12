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
    print(datelist)
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
    file_name =  'house'+'.json'
    sold_name = 'sold.json'

    house_list = {}
    house_json_list = []
    id_list = []
    f = open("house_id.txt",'a+')

    def open_spider(self,spider):
        #连接不同数据库
        fp = open("house_id.txt",'r+')
        temp_id_list = list(map(myStrip,fp.readlines()))
        fp.close()
        i = 0

        for item in temp_id_list:
            spider.house_id_dict[item] = i
            i+=1

        if spider.name =="zoopla_on_sale":
            self.file = open(self.file_name, 'a+') 
        else:
            #spider is soldSPider
            date = set_timezone("Europe/London")
            #create update file
            update_file = "%s_update.json"%date
            self.update_fp= open(update_file,"a+")
            #create solditem file
            self.file = open(self.sold_name,'a')

    def process_item(self, item, spider):
        #不同的spider 进行不同的清洗和 append
        if spider.name =="zoopla_on_sale":
            self.id_list.append(item['listing_id']+"\n")
            #self.house_list[item['listing_id']]=dict(item)
            house_json = json.dumps(dict(item), ensure_ascii=False) + '\n'
            self.house_json_list.append(house_json)
            #self.house_list.clear()
            if len(self.id_list)==256:
                for i in range(len(self.id_list)):
                    self.f.write(self.id_list[i])
                    self.file.write(self.house_json_list[i])
                self.id_list.clear()
                self.house_json_list.clear()
        else:
            if isinstance(item,SoldItem):
                #delete sold id
                del spider.house_id_dict[item['house_id']]
                self.house_list[item['house_id']]=dict(item)
                sold_house_info= json.dumps(self.house_list, ensure_ascii=False) + '\n'
                self.file.write(sold_house_info)
                self.house_list.clear()
            else:
                update_json= json.dumps(dict(item), ensure_ascii=False) + '\n'
                self.update_fp.write(update_json)

        # this means if the crawler now traverse to the house that match the
        # same house in local storage, stop the crawler

        """
        if not os.path.isfile(file_name):
            with open(file_name, 'w') as f:
                line = json.dumps(dict(item), ensure_ascii=False) + '\n'
                f.write(line)
        else:
            with open(file_name, 'a') as f:
                line = json.dumps(dict(item), ensure_ascii=False) + '\n'
                f.write(line)
                """
        return item
    def close_spider(self, spider):
        self.file.close()
        if spider.name == "zoopla_on_sale":
            self.f.close()
        else:
            self.update_fp.close()
            self.house_id_fp = open("house_id.txt","w+")
            for item in spider.house_id_dict:
                self.house_id_fp.write(item+"\n")
            self.house_id_fp.close()
        #1.写入不同的数据表
