import region_extractor 
import json_reader 
import math
from statistics import median

homo_attribute = ["num_bath","num_bed","price","month_view","coordinate","property_type"]
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
    geo_distance = math.sqrt((float(house_info["coordinate"][0])-float(neighbour["coordinate"][0]))**2 + (float(house_info["coordinate"][1])-float(neighbour["coordinate"][1]))**2)
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


def estimate_price(houseid,sale_type,estimate_type):
    region_houses_dict = locate_range(houseid,estimate_type+"_region/",sale_type)
    house_info = extract_house_info(houseid)
    if sale_type==estimate_type:
        neighbours = house_KNN(house_info,region_houses_dict,10,homo_attribute)
    else:
        neighbours = house_KNN(house_info,region_houses_dict,10,hetero_attribute)
    return neighbours


neighbours = estimate_price("45101554","sale","rent")
print(calculate_mid_price(neighbours))
