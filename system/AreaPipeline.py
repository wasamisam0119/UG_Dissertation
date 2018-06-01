import pandas as pd
from DataFetcher import DataFetcher 
from sqlalchemy import create_engine  
import re
dropping_feature = ['crawling_time','top3near_by']
groupby_feature = ["region","property_type"]
merge_key = ["region","property_type"]
citypattern = re.compile("[A-Za-z]+")

    
class AreaPipeline(object):
    def __init__(self,area_config):
        self.read_config(area_config)
        self.city = pd.read_csv("postcode.csv")
        
        #Fetch the already sold and rented house
        self.s = DataFetcher("sale",self.pattern)
        self.r = DataFetcher("rent",self.pattern)
        
    def switch_area(self,area_config):
        if self.pattern[-1].isdigit():
            with open(area_config,"w") as f:
                f.write("NG")
            self.pattern = "NG"
            self.database_name = "SuperArea"
        else:
            with open(area_config,"w") as f:
                f.write("NG7")
            self.pattern = "NG7"
            self.database_name = "Area"

        self.s = DataFetcher("sale",self.pattern)
        self.r = DataFetcher("rent",self.pattern)

    def read_config(self,area_config):
        with open(area_config,"r") as r:
                self.pattern = r.read().splitlines()[0]
                if self.pattern[-1].isdigit():
                    self.database_name = "Area"
                else:
                    self.database_name = "SuperArea"
                    

    def area_process(self):

        s_df = pd.DataFrame(self.s.retrieve_sold_info())
        r_df = pd.DataFrame(self.r.retrieve_sold_info())

        s_df = s_df[(s_df.num_bed>0)]
        r_df = r_df[(r_df.num_bed>0)]

        #drop features 
        s_df = s_df.drop(dropping_feature,axis = 1)
        r_df = r_df.drop(dropping_feature,axis = 1)

        area_s_df = s_df.groupby(groupby_feature,as_index=False)['speed','month_view','price','first_published_date']\
                        .agg({'speed':'mean','month_view':'mean','price':'mean','first_published_date':'count'}).round(0)

        area_r_df = r_df.groupby(groupby_feature,as_index=False)['speed','month_view','price','first_published_date']\
                        .agg({'speed':'mean','month_view':'mean','price':'mean','first_published_date':'count'}).round(0)

        #area infomation
        area_s_df.columns = groupby_feature+["sale_speed","s_monthview","sale_price","sale_count"]
        area_r_df.columns = groupby_feature+["rent_speed","r_monthview","rent_price","rent_count"]
        #merge sale field and rental field
        area_df = pd.merge(area_s_df,area_r_df,on = merge_key)
        #calculate Price to Rent ratio
        area_df['PTR'] = (12*area_df['rent_price']/area_df['sale_price']).round(5)

        #add column city
        area_df['city'] = area_df.apply(lambda row: matchcity(self.city,row),axis = 1)
        return area_df

def matchcity(city_map,row):
    region = citypattern.match(row.region).group(0)
    return city_map.values[city_map['postcode'] ==region][0][1]



"""
t = AreaPipeline("area_config.txt")
area_df = t.area_process()
#%run area_info_retri.py
password = ""
#engine =create_engine('mysql+pymysql://root:%s@localhost:3306/G53DT?charset=utf8'%password)
engine =create_engine('mysql+pymysql://root:@localhost:3306/G53DT?charset=utf8')
area_df.to_sql("SuperArea",engine,if_exists = 'replace')
"""
