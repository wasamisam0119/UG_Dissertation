import json
import knn
from datetime import datetime
import time
import region_extractor
from knn import locate_range
from pre_define import train_features
from pre_define import weights
from AreaPipeline import matchcity,citypattern
import pandas as pd

house_extracted = "sale_extracted.json"
log = "user_pipe.log"
config = "area_config.txt"

class KNN_Middleware(object):

    def __init__(self):
        self.city = pd.read_csv("postcode.csv")
        #self.filename = "sale_extracted.json"
        #self.log = "user_pipe.log"

    def KNN_process(self,house_extracted_name,log):
        with open(house_extracted_name,"r") as r:
            for item in r:
                info = json.loads(item)
                houses_info = pd.DataFrame(info).T
                
        houses_info['crawling_time'] = pd.to_datetime(houses_info['crawling_time'],format='%d-%m-%Y')

        last_time =self.reading_history(log)

        new_added_house = houses_info[(houses_info.crawling_time>last_time)]
        estimate_type = "rent"
        sale_type = "sale"
        self.write_time(log)
        if new_added_house.shape[0]<=1:
            return pd.DataFrame()
        else:
            #new_added_house = new_added_house[:5].copy() 
            
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
            new_added_house['PTR'] = (new_added_house['estimate_price']/new_added_house['price']).astype(float).round(5)
            new_added_house['postcode'] = new_added_house.apply(lambda row: self.reverse_postcode(row['postcode']),axis =1)  
            new_added_house['region'] =new_added_house.apply(lambda row: row['postcode'].split()[0],axis = 1)  
            new_added_house['city'] = new_added_house.apply(lambda row: matchcity(self.city,row),axis = 1)
            new_added_house = new_added_house.drop(['coordinate','top3near_by'],axis = 1)
            #print(new_added_house)
        return new_added_house



    def reverse_postcode(self,postcode):
        t = postcode.split()
        return t[1]+" "+t[0]

    def reading_history(self,log):
        with open(log,"r") as r:
            last_time = r.read().splitlines()[0]
        last_time = datetime.strptime(last_time,"%Y-%m-%d %H:%M:%S")
        return last_time
        
    def write_time(self,log):
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        with open(log,"w") as r:
            r.writelines(current_time)

    def knn_apply(self,estimate_type,sale_type,house):
        region_list = locate_range(house['postcode'],estimate_type+"_region/",sale_type)
        neighbours = pd.DataFrame(region_list)
        if len(region_list) ==0:
            return neighbours 
        neighbours = neighbours.drop(neighbours[neighbours['listing_id']==house['listing_id']].index )
        K_neighbours = knn.house_KNN(house,neighbours,5,train_features,knn.calculate_weightedDistance,weights)
        #return (K_neighbours['price'].mean(),K_neighbours['listing_id']) 
        return K_neighbours

    def get_estimate(self,neighbours):
        return neighbours['price'].mean()


"""
def knn_apply1(estimate_type,sale_type,new_added_house):
    estimate_price = []
    i = 0
    for index,house in new_added_house.iterrows():
        i+=1
        region_list = locate_range(house['postcode'],estimate_type+"_region/",sale_type)
        neighbours = pd.DataFrame(region_list)
        neighbours.drop(neighbours[neighbours['listing_id']==house['listing_id']].index )

        K_neighbours = knn.house_KNN(house,neighbours,5,train_features,knn.calculate_weightedDistance,weights)
        print(K_neighbours)
        print(K_neighbours.shape)
        estimate_price.append(K_neighbours['price'].mean())
        if i>4:
            break

        #new_added_house['neighbours'] = new_added_house.apply(lambda row: houseKNN)

    estimate_price = pd.DataFrame(estimate_price) 
    new_added_house['estimate_price'] = estimate_price
    return new_added_house

"""
#new_added_house['neighbour'].dtype(str)
knnMidd = KNN_Middleware()
new_added_house = knnMidd.KNN_process(house_extracted,log)
    #if there is new added house, write to database
from sqlalchemy import create_engine  
if new_added_house.shape[0] >0:
    engine =create_engine('mysql+pymysql://root:@localhost:3306/G53DT?charset=utf8')
    new_added_house.to_sql("Houses",engine,if_exists = 'replace',index_label = "listing_id",index =False)


