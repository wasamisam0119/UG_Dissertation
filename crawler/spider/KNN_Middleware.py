import json
import os
import knn
from datetime import datetime,timedelta
import time
import region_extractor
from knn import locate_range
from pre_define import train_features
from pre_define import weights
from AreaPipeline import matchcity,citypattern
import json_reader 
import pandas as pd
import sys
sys.path.append("spiders")
from sysMem import getSysMemory

house_extracted = "sale_extracted.json"
log = "user_pipe.log"
config = "area_config.txt"
path = "./sale_region/"
#passwd = "G53psysz3"

class KNN_Middleware(object):

    def __init__(self):
        self.city = pd.read_csv("postcode.csv")
        self.region_list = os.listdir(path)
        if ".DS_Store" in self.region_list:
            self.region_list.remove(".DS_Store")
        #self.filename = "sale_extracted.json"
        #self.log = "user_pipe.log"

    def KNN_process(self,house_extracted_name,log):
        if self.daily_check(log):
            return pd.DataFrame() 
        new_added_region_house = []
        for region in self.region_list:
            houses_info = list(json_reader.json_read(path,region)[0].values())[0]
            houses_info = pd.DataFrame(houses_info)

            try:
                houses_info['crawling_time'] = pd.to_datetime(houses_info['crawling_time'],format='%d-%m-%Y')
            except KeyError as e:
                print(region)
                continue

            time_array=self.reading_history(log)
            last_time = time_array[0]
            limit_time = time_array[1]
            new_added_house = houses_info[(houses_info.crawling_time>=last_time)&(houses_info.crawling_time<limit_time)].copy()
            
            estimate_type = "rent"
            sale_type = "sale"
            #print("read house current memory is %d"%getSysMemory())
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if new_added_house.shape[0]<=1:
                continue
            else:
                print(new_added_house.shape[0])
                new_added_house = new_added_house[(new_added_house.num_bed>0)]
                #new_added_house['neighbour'] = new_added_house.apply(lambda row:self.knn_apply(estimate_type,sale_type,row),axis = 1)
                new_added_house['lat'] =new_added_house.apply(lambda row: row['coordinate'][0],axis = 1)
                new_added_house['lon'] =new_added_house.apply(lambda row: row['coordinate'][1],axis = 1)
                new_added_house['listing_id']=new_added_house['listing_id'].astype(int)
                listing_id_set = []
                estimate_price_set = []
                index_list = []
                i = 0
                for index,house in new_added_house.iterrows():
                    K_neighbour = self.knn_apply(estimate_type,sale_type,house)
                    if K_neighbour.empty:
                        index_list.append(i)
                    else:
                        listing_id_set.append(K_neighbour['listing_id'].values.tolist())
                        estimate_price_set.append(K_neighbour['price'].mean())
                    i+=1
                new_added_house=new_added_house.drop(new_added_house.index[index_list])
                new_added_house =new_added_house.assign(neighbour = pd.Series(listing_id_set).values)
                new_added_house =new_added_house.assign(estimate_price = pd.Series(estimate_price_set).values)
                new_added_house['neighbour'] = new_added_house['neighbour'].astype(str)
                new_added_house['PTR'] = (12*new_added_house['estimate_price']/new_added_house['price']).astype(float).round(5)
                new_added_house['postcode'] = new_added_house.apply(lambda row: self.reverse_postcode(row['postcode']),axis =1)  
                new_added_house['region'] =new_added_house.apply(lambda row: row['postcode'].split()[0],axis = 1)  
                new_added_house['city'] = new_added_house.apply(lambda row: matchcity(self.city,row),axis = 1)
                new_added_house = new_added_house.drop(['coordinate','top3near_by'],axis = 1)
                #print(new_added_house)
                new_added_region_house.append(new_added_house)

        self.write_time(log)
        if len(new_added_region_house)==0:
            return pd.DataFrame() 
        else:
            new_added_house = pd.concat(new_added_region_house)
            return new_added_house  



    def daily_check(self,log):
        time_array = self.reading_history(log)
        if datetime.now().strftime('%Y-%m-d') ==time_array[0]:
            print("Already checked today %s"%time_array[0])
            return True

    def reverse_postcode(self,postcode):
        t = postcode.split()
        return t[1]+" "+t[0]

    def reading_history(self,log):
        with open(log,"r") as r:
            time_array= r.read().splitlines()
            last_time = time_array[0]
            limit_time = time_array[1]
        last_time = datetime.strptime(last_time,"%Y-%m-%d")
        limit_time = datetime.strptime(limit_time,"%Y-%m-%d")
        return (last_time,limit_time)
        
    def write_time(self,log):
        current_time = datetime.now().strftime("%Y-%m-%d")
        limit_time = (datetime.now()+timedelta(days = 3)).strftime("%Y-%m-%d")
        with open(log,"w") as r:
            r.write(current_time+"\n")
            r.write(limit_time+"\n")

    def knn_apply(self,estimate_type,sale_type,house):
        region_list = locate_range(house['postcode'],estimate_type+"_region/",sale_type)
        neighbours = pd.DataFrame(region_list)
        if len(region_list) ==0:
            return neighbours 
        neighbours = neighbours.drop(neighbours[neighbours['listing_id']==house['listing_id']].index )
        K_neighbours = knn.house_KNN(house,neighbours,5,train_features,knn.calculate_weightedDistance,weights)
        return K_neighbours

    def get_estimate(self,neighbours):
        return neighbours['price'].mean()

"""
knnMidd = KNN_Middleware()
new_added_house = knnMidd.KNN_process(house_extracted,log)
print("finished")
    #if there is new added house, write to database
from sqlalchemy import create_engine  
if new_added_house.shape[0] >0:
    engine =create_engine('mysql+pymysql://root:%s@localhost:3306/G53DT?charset=utf8'%passwd)
    new_added_house.to_sql("Houses",engine,if_exists = 'append',index_label = "listing_id",index =False)
"""
