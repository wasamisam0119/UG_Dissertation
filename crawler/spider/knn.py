import region_extractor 
import sys
import os
import json_reader 
import math
from statistics import median
import pandas as pd

import geopy.distance


weights = pd.DataFrame([  2.15520417*10**-2,   1.19257808*10**-2,   3.14956906*10**-7,   7.93325839*10**-6]).T

def clean_noise(house_list,minimum_price,house_type):
    house_list = pd.DataFrame(house_list)
    rows= house_list.shape[0]
    if rows >0:        
        house_list = house_list[(house_list.price>minimum_price) & (house_list.property_type.isin(house_type)) &(house_list.num_bed>0)]
    return house_list

def house_KNN(house_info,neighbours,K,attribute_list,distance_method,weights):
    neighbours['distance'] = neighbours.apply(lambda row: distance_method(house_info,row,attribute_list,weights),axis=1)
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

def calculate_weightedDistance(house_info,neighbour,attribute,weights):
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

def calculate_Distance(house_info,neighbour,attribute,weights):
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

#postcode = locate_postcode(house_id,saletype)

def locate_range(postcode,region_path,saletype):
    region = region_extractor.extract_region(postcode)
    print(region)
    region_houses = json_reader.json_read(region_path,region+".json")

    region_houses_dict = region_houses[0]
    if len(region_houses_dict) ==0:
        return []
    else:
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
