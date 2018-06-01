import json
import os
import sys
import re
import region_extractor

citypattern = re.compile("[A-Za-z]+")

region =[ 
"AB",
"AL",
"B",
"BA",
"BB",
"BD",
"BH",
"BL",
"BN",
"BR",
"BS",
"BT",
"CA",
"CB",
"CF",
"CH",
"CM",
"CO",
"CR",
"CT",
"CV",
"CW",
"DA",
"DD",
"DE",
"DG",
"DH",
"DL",
"DN",
"DT",
"DY",
"E",
"EC",
"EH",
"EN",
"EX",
"FK",
"FY",
"G",
"GL",
"GU",
"HA",
"HD",
"HG",
"HP",
"HR",
"HS",
"HU",
"HX",
"IG",
"IP",
"IV",
"KA",
"KT",
"KW",
"KY",
"L",
"LA",
"LD",
"LE",
"LL",
"LN",
"LS",
"LU",
"M",
"ME",
"MK",
"ML",
"N",
"NE",
"NG",
"NN",
"NP",
"NR",
"NW",
"OL",
"OX",
"PA",
"PE",
"PH",
"PL",
"PO",
"PR",
"RG",
"RH",
"RM",
"S",
"SA",
"SE",
"SG",
"SK",
"SL",
"SM",
"SN",
"SO",
"SP",
"SR",
"SS",
"ST",
"SW",
"SY",
"TA",
"TD",
"TF",
"TN",
"TQ",
"TR",
"TS",
"TW",
"UB",
"W",
"WA",
"WC",
"WD",
"WF",
"WN",
"WR",
"WS",
"WV",
"YO",
"ZE"]

region_set = {}
for item in region:
    region_set[item] = []

house_info = sys.argv[1]
folder = sys.argv[2]
print (house_info)

with open(house_info,"r") as r:
    for item in r:
        info = json.loads(item)
        for house_id,house in info.items():
            outpostcode = region_extractor.extract_region(house["postcode"])
            city_postcode = citypattern.search(outpostcode).group(0) 
            if city_postcode in region:
                region_set[city_postcode].append(house)
                

for area, area_houses in region_set.items():
    with open("%s_region/%s.json"%(folder,area),"w+") as f:
        area_dict = {}
        area_dict[area] = area_houses
        f.write(json.dumps(area_dict,ensure_ascii=False))



            




