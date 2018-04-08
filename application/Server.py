import pandas as pd
from sqlalchemy import create_engine
import os
import re

path =os.path.dirname(__file__) + "/postcode.csv"
pattern = re.compile("[A-Za-z]+")


class Server(object):

    def __init__(self):
        print(os.path.dirname(__file__))
        self.postcode_set = pd.read_csv(path)
        self.engine = create_engine('mysql+pymysql://root:@localhost:3306/G53DT?charset=utf8')

    def parse_sentence(self, name):
        if name in self.postcode_set['postcode'].values:
            return name

        elif name in self.postcode_set['city'].values:
            return name

        elif pattern.match(name).group(0) in self.postcode_set['postcode'].values:
            return name
        else:
            return "Value Error"

    def fetch_area_info(self, name,house_type):
        if name in self.postcode_set['city'].values:
            print(name)
            sql_query = "SELECT * FROM G53DT.SuperArea where city = %s AND property_type = %s ORDER BY PTR DESC;"

        else:
            sql_query = "SELECT * FROM G53DT.Area where region LIKE %s AND property_type = %s ORDER BY PTR DESC;"
            name = "%"+name+"%"
        t = pd.read_sql(sql_query, self.engine,params=[name,house_type])
        return t

    def fetch_house_info(self, name,house_type):
        if name in self.postcode_set['city'].values:
            sql_query = "SELECT * FROM G53DT.Houses WHERE city = %s AND property_type = %s ORDER BY PTR DESC LIMIT 10;"

        else:
            sql_query = "SELECT * FROM G53DT.Houses WHERE region LIKE %s AND property_type = %s ORDER BY PTR DESC LIMIT 10;"
            name = "%"+name+"%"
        t = pd.read_sql(sql_query, self.engine,params = [name,house_type])

        return t

