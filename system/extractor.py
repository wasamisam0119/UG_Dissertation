import json

class Extractor(object):
    """
    listing_id
    {id:{info}}
    postcode
    crawling_time
    first_published_date
    num_of_bathrooms
    num_of_bedrooms
    property_type
   """ 
    
    def __init__(self,filename):
        if "rent" in filename:
            self.attr = "rent"
        else:
            self.attr = "sale"
        self.f = open(filename,"r")
        self.house_dict = {}
        self.outputname = filename[:4]+"_extracted.json"
        self.property_set = ["end terrace","terraced","semi-detached","detached","mews house",
"flat",
"maisonette",
"bungalow",
"town house",
"cottage",
"farm",
"barn",
"mobile",
"static",
"land",
"studio", 
"block of flats", "office"]
        
    def extract(self):
        property_type = ""
        for line in self.f:
            house = json.loads(line)
            for item in self.property_set:
                if item in house["title"]:
                    property_type = item
                    break
            if self.attr == "rent":
                try:
                    if "first_published_date" not in house:
                        try:
                            self.house_dict[house['listing_id']] = {"listing_id":house["listing_id"],"crawling_time":house['crawling_time'],"postcode":house['postcode'],"first_published_date":-1,"num_bath":house['num_of_bathrooms'],"num_bed":house["num_of_bedrooms"],"property_type":property_type,"price":house["monthly_price"],"coordinate":[float(house["coordinate"][0]),float(house["coordinate"][1])],"month_view": house["month_view"],"top3near_by":house["top3near_by"]}
                        except KeyError as e:
                            continue
                    else:
                        try:
                            self.house_dict[house['listing_id']] = {"listing_id":house["listing_id"],"crawling_time":house['crawling_time'],"postcode":house['postcode'],"first_published_date":house['first_published_date'],"num_bath":house['num_of_bathrooms'],"num_bed":house["num_of_bedrooms"],"property_type":property_type,"price":house["monthly_price"],"coordinate":[float(house["coordinate"][0]),float(house["coordinate"][1])],"month_view": house["month_view"],"top3near_by":house["top3near_by"]}
                        except KeyError as e:
                            continue
                except ValueError as e:
                    print(house["coordinate"])
                    continue

            else:
                try:

                    if "first_published_date" not in house:
                        try:
                            self.house_dict[house['listing_id']] = {"listing_id":house["listing_id"],"crawling_time":house['crawling_time'],"postcode":house['postcode'],"first_published_date":-1,"num_bath":house['num_of_bathrooms'],"num_bed":house["num_of_bedrooms"],"property_type":property_type,"price":house["price"],"coordinate":[float(house["coordinate"][0]),float(house["coordinate"][1])],"month_view": house["month_view"],"top3near_by":house["top3near_by"]}
                        except KeyError as e:
                            continue

                    else:
                        try:
                            self.house_dict[house['listing_id']] = {"listing_id":house["listing_id"],"crawling_time":house['crawling_time'],"postcode":house['postcode'],"first_published_date":house['first_published_date'],"num_bath":house['num_of_bathrooms'],"num_bed":house["num_of_bedrooms"],"property_type":property_type,"price":house["price"],"coordinate":[float(house["coordinate"][0]),float(house["coordinate"][1])],"month_view": house["month_view"],"top3near_by":house["top3near_by"]}
                        except KeyError as e:
                            continue
                except ValueError as e:
                    print(house["coordinate"])
                    continue



    def output(self):
        of = open(self.outputname,"w")
        of.write(json.dumps(self.house_dict))
        of.close()
        self.f.close()





            
sale_ex = Extractor("sale_house.json")
sale_ex.extract()
sale_ex.output()

rent_ex = Extractor("rent_house.json")
rent_ex.extract()
rent_ex.output()


