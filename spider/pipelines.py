# -*- coding: utf-8 -*-
import os
import json
import re
import sys

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

class SpiderPipeline(object):
    def process_item(self, item, spider):
        file_name = spider.name + '.json'
        item['added_time'] = date_filter(item['added_time'])
        # this means if the crawler now traverse to the house that match the
        # same house in local storage, stop the crawler
        if spider.local_house_info[0] == item['added_time'] and spider.local_house_info[1] == item['price']:
            sys.exit()
        else:
            if not os.path.isfile(file_name):
                with open(file_name, 'w') as f:
                    line = json.dumps(dict(item), ensure_ascii=False) + '\n'
                    f.write(line)
            else:
                with open(file_name, 'a') as f:
                    line = json.dumps(dict(item), ensure_ascii=False) + '\n'
                    f.write(line)
            return item
