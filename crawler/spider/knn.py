import region_extractor 
import sys

import json_reader 
import math
from statistics import median

homo_attribute = ["num_bath","num_bed","price","month_view","coordinate","property_type"]
train_features = ["num_bath","num_bed","month_view","property_type","coordinate"]
#= ["num_bath","bed_dis","price","month_view_dis","coordinate_dis","property_type_dis"]
hetero_attribute = ["num_bath","num_bed","month_view","coordinate","property_type"]

def house_KNN(house_info,neighbours,K,attribute_list):
    neighbour_list = []
    for neighbour in neighbours:
        #print(neighbour)
        neighbour_list.append((calculate_weightedDistance(house_info,neighbour,attribute_list),neighbour))
    K_neighbours_list = sorted(neighbour_list,key = lambda t:t[0],reverse = False)[:K]
    print(K_neighbours_list)
    return K_neighbours_list

def calculate_weightedDistance(house_info,neighbour,attribute):
    distance_list = []
    distance = 0
    for i in range(len(attribute)-2):
        distance_list.append(math.sqrt((house_info[attribute[i]]-neighbour[attribute[i]])**2))
    try:
        geo_distance = math.sqrt((float(house_info["coordinate"][0])-float(neighbour["coordinate"][0]))**2 + (float(house_info["coordinate"][1])-float(neighbour["coordinate"]    [1]))**2)
    except ValueError as ve:
        geo_distance = 0.1
    distance_list.append(geo_distance)
    #property type
    if house_info["property_type"] == neighbour["property_type"]:
        distance_list.append(0)
    else:
        distance_list.append(1)
    for feature_distance in distance_list:
        distance += feature_distance*gaussian_kernel(feature_distance)
    return distance

def gaussian_kernel(feature_distance):
    l = 2
    return math.exp(-(feature_distance)**2/l)

def locate_postcode(house_id,saletype):
    info_container = json_reader.json_read("./",saletype+"_extracted.json")
    info_dict = info_container[0]
    
    if house_id in info_dict:
        return info_dict[house_id]["postcode"]
    else:
        return "not find"


#house id should be a string
#{SW:[houseinfo,houseinfo,houseinfo]}

def locate_range(house_id,region_path,saletype):
    postcode = locate_postcode(house_id,saletype)
    region = region_extractor.extract_region(postcode)
    region_houses = json_reader.json_read(region_path,region+".json")
    region_houses_dict = region_houses[0]
    region_houses = region_houses_dict.values()
    return list(region_houses)[0]
        
def extract_house_info(house_id):
    houses = json_reader.json_read("./","sale_extracted.json")[0]
    if house_id in houses:
        return houses[house_id]
    else:
        houses = json_reader.json_read("./","rent_extracted.json")[0]
        if house_id in houses:
            return houses[house_id]
        else:
            return 0

def calculate_mid_price(neighbours):
    price_list = []
    for house in neighbours:
        price_list.append(house[1]["price"])
    return median(price_list)


#data = json_reader.json_read("./","rented.json")[0]
import pandas as pd
def Euclidean_distance(x1,x2):
    d = 0
    for feature in x1:
        if type(x1[feature]) is list:
            d += (Euclidean_distance(x1[feature],x2[feature]))**2
        else:
            d += (x1[feature]-x2[feature])**2
    return math.sqrt(d)

def squareDiffer(x1,x2):
    #coordinates
    if type(x1) is list:
        s = 0
        try:
            for i in range(len(x1)):
                s += (float(x1[i])-float(x2[i]))**2
        except ValueError as ve:
            s = 0.1
        return s
    #property_type
    elif type(x1) is str:
        if x1 == x2:
            return 0
        elif x1 in x2 or x2 in x1:
            return 0.5
        else:
            return 1
    #other features
    else:
        return (x1-x2)**2

from sklearn import preprocessing
def prepareTrainingdata(houseid,sale_type,estimate_type):
    whole_data_set = []
    house_distance_set = []
    price_difference_set = []
    region_houses_list = locate_range(houseid,estimate_type+"_region/",sale_type)
    print(len(region_houses_list))
    for i, house_info in enumerate(region_houses_list):
        #house_info = extract_house_info(house)
        for j in range(i+1,len(region_houses_list)):
            
            house = region_houses_list[i]
            house_d_features = []
            #print(house_info["listing_id"])

            price_difference = (house["price"] - house_info["price"])**2
            #house_d_features.append(house["listing_id"])
            for feature in train_features:
                house_d_features.append(squareDiffer(house[feature],house_info[feature]))

            house_distance_set.append(house_d_features)
            price_difference_set.append(price_difference)
    min_max_scaler = preprocessing.MinMaxScaler()
    examples= min_max_scaler.fit_transform(pd.DataFrame(house_distance_set))
    #examples = preprocessing.scale(pd.DataFrame(house_distance_set))
    labels = pd.DataFrame(price_difference_set)
    
    return (examples,labels)
#需要把每个房子
#print(extract_house_info("27274665"))
from sklearn.model_selection import train_test_split
features, target = prepareTrainingdata("27274665","rent","rent")
print(features.shape)
X_train, X_test, y_train, y_test = train_test_split(features, target,
                                                    test_size=0.33,
                                                    random_state=42)
from sklearn import linear_model
lr = linear_model.LinearRegression()
model = lr.fit(X_train, y_train)
predictions=model.predict(X_test)

from sklearn.metrics import mean_squared_error
print('RMSE is: %d'%mean_squared_error(y_test,predictions))
print(model.score(X_test,y_test))




def estimate_price(houseid,sale_type,estimate_type):
    region_houses_dict = locate_range(houseid,estimate_type+"_region/",sale_type)
    house_info = extract_house_info(houseid)
    print(region_houses_dict)
       
    
    if sale_type==estimate_type:
        neighbours = house_KNN(house_info,region_houses_dict,10,homo_attribute)
    else:
        neighbours = house_KNN(house_info,region_houses_dict,10,hetero_attribute)
    return neighbours

#neighbours = estimate_price("32802781","rent","rent")

#print(calculate_mid_price(neighbours))

