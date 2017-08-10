# -*- coding: utf-8 -*-
import os
import json
import re
import sys
import time
import pymysql

def format_add_time(originString):
    dateRegex = re.compile("\d{2}[a-z]+\s[a-z]+\s20\d{2}")
    if len(dateRegex.findall(originString))>0:
        formattedTime = dateRegex.findall(originString)[0]
    else:
        formattedTime = ""
    return formattedTime

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

class SoldPipeline(object):
    id_list = []
    def open_spider(self,spider):
        pass


    def close_spider(self,spider):
        #写到另一张表里去
        pass

class SpiderPipeline(object):
    file_name =  'house'+'.json'
    sold_name = 'sold.json'
    house_list = {}
    id_list = []
    f = open("house_id.txt",'a+')
    def open_spider(self,spider):
        #连接不同数据库
        self.id_list =self.f.readlines()
        i = 0
        for item in self.id_list:
            spider.house_id_dict[item] = i
            i+=1
        if spider.name =="zoopla_on_sale":
            self.file = open(self.file_name, 'a') 
        else:
            self.file = open(self.sold_name,'a')

    def process_item(self, item, spider):
        #不同的spider 进行不同的清洗和 append
        if spider.name =="zoopla_on_sale":
            self.id_list.append(item['listing_id']+"\n")
            self.house_list[item['listing_id']]=dict(item)
            house_json = json.dumps(self.house_list, ensure_ascii=False) + '\n'
            self.file.write(house_json)
            self.house_list.clear()
            if len(self.id_list)==10:
                for item in self.id_list:
                    self.f.write(item)
                self.id_list.clear()
                print("sssssssssssssssssssssssssss")
        else:
            del spider.house_id_dict[item['house_id']]
            self.house_list[item['house_id']]=dict(item)
            sold_house_info= json.dumps(self.house_list, ensure_ascii=False) + '\n'
            self.file.write(sold_house_info)

            pass
        # this means if the crawler now traverse to the house that match the
        # same house in local storage, stop the crawler

        """
        if spider.local_house_info[0] == item['added_time'] and spider.local_house_info[1] == item['price']:
            sys.exit()
        else:
            """
        
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
        if spider.name == "zoopla_on_sale":
            self.f.close()
        else:
            for item in spider.house_id_dict:
                self.delete_list_fp.write(item+"\n")
            self.delete_list_fp.close()
        self.file.close()
        #1.写入不同的数据表
        #
        pass

