import region_extractor 
import sys
import os
import json_reader 
import math
from statistics import median
import pandas as pd
import geopy.distance

train_features = ["num_bath","num_bed","month_view","coordinate"]
weights = pd.DataFrame([  2.15520417*10**-2,   1.19257808*10**-2,   3.14956906*10**-7,   7.93325839*10**-6]).T

def clean_noise(house_list,minimum_price,house_type):

    
    house_list = pd.DataFrame(house_list)
    house_list = house_list[(house_list.price>minimum_price) & (house_list.property_type.isin(house_type)) & (house_list.num_bed>0)]
    return house_list

def house_KNN(house_info,neighbours,K,attribute_list,distance_method):
    neighbours['distance'] = neighbours.apply(lambda row: distance_method(house_info,row,attribute_list),axis=1)
    neighbours = neighbours.sort_values('distance')
   
    K_neighbours_list = neighbours[:K].copy()
    return K_neighbours_list
    """
    for neighbour in neighbours:
        print(neighbour)
        print(house_info)
        neighbour_list.append((calculate_weightedDistance(house_info,neighbour,attribute_list),neighbour))
    """
    #K_neighbours_list = sorted(neighbour_list,key = lambda t:t[0],reverse = False)[:K]
    #K_neighbours_list
    #print(K_neighbours_list)
    #print(neighbours.head())
    #return K_neighbours_list
#def estimate_price(K_neighbours_list):

def calculate_weightedDistance(house_info,neighbour,attribute):
    distance_list = []
    distance = 0
    geo_dis = geopy.distance.vincenty(house_info["coordinate"],neighbour["coordinate"]).m
    for feature in attribute:
        if feature == "coordinate":
            distance_list.append(geo_dis)
        else:
            distance_list.append(squareDiffer(house_info[feature],neighbour[feature]))
    distance_list = pd.DataFrame(distance_list)
    return weights.dot(distance_list)[0][0]

def calculate_Distance(house_info,neighbour,attribute):
    distance_list = []
    distance = 0
    geo_dis = geopy.distance.vincenty(house_info["coordinate"],neighbour["coordinate"]).m
    for feature in attribute:
        if feature == "coordinate":
            distance_list.append(geo_dis)
        else:
            distance_list.append(squareDiffer(house_info[feature],neighbour[feature]))
    distance_list = pd.DataFrame(distance_list)
    return distance_list.sum()

                    

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
    """
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
        """
    return (x1-x2)**2

def prepareTrainingdata(region,sale_type,estimate_type):
    whole_data_set = []
    house_distance_set = []
    price_difference_set = []
    region_houses_list = list(json_reader.json_read(estimate_type+"_region/",region)[0].values())[0]
    #region_houses_list = locate_range(houseid,estimate_type+"_region/",sale_type)
    for i, house_info in enumerate(region_houses_list):
        #house_info = extract_house_info(house)
        for j in range(i+1,len(region_houses_list)):
            
            house = region_houses_list[j]
            house_d_features = []
            #print(house_info["listing_id"])

            price_difference = math.sqrt((house["price"] - house_info["price"])**2)
            #sys.exit()
            #house_d_features.append(house["listing_id"])
            for feature in train_features:
                house_d_features.append(squareDiffer(house[feature],house_info[feature]))

            house_distance_set.append(house_d_features)
            price_difference_set.append(price_difference)
    examples= pd.DataFrame(house_distance_set)
    #examples = preprocessing.scale(pd.DataFrame(house_distance_set))
    labels = pd.DataFrame(price_difference_set)
    return (examples,labels)


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


def readData(filename):
    region_houses_list = list(json_reader.json_read(estimate_type+"_region/",region)[0].values())[0]
    return region_houses_list
