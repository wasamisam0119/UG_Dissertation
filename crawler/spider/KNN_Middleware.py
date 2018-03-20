import json
import knn
from datetime import datetime
import time
import region_extractor
from knn import locate_range
from pre_define import train_features
from pre_define import weights
import pandas as pd

class KNN_Middleware(object):

    def __init__(self):

        pass
        #self.filename = "sale_extracted.json"
        #self.log = "user_pipe.log"

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
        neighbours.drop(neighbours[neighbours['listing_id']==house['listing_id']].index )
        K_neighbours = knn.house_KNN(house,neighbours,5,train_features,knn.calculate_weightedDistance,weights)
        return K_neighbours['price'].mean() 


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




"""
两个func：
把没用的attribute drop掉 
写入数据库
"""





