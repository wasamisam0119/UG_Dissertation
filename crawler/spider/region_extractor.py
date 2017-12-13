
import json
import re

citypattern = re.compile("[A-Za-z]+")

def extract_region(postcode):
    postcode_split = postcode.split()
    region  = citypattern.search(postcode_split[1]).group(0)
    return region

