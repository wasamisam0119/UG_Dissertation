import time
import os
from KNN_Middleware import KNN_Middleware 
from sqlalchemy import create_engine  
from AreaPipeline import AreaPipeline

house_extracted = "sale_extracted.json"
log = "user_pipe.log"
config = "area_config.txt"
password = "G53psysz3"


while True:

    #check on-sale houses and crawling new houses
    os.system("python salecheck_regular.py 1>salecheckoutput 2>salecheckerror")

    #extract useful data and classify houses into regions
    os.system("python auto-update.py")

    #start KNN process for new crawled houses 
    knnMidd = KNN_Middleware()
    new_added_house = knnMidd.KNN_process(house_extracted,log)
    #if there is new added house, write to database
    if new_added_house.shape[0] >0:
        engine =create_engine('mysql+pymysql://root:%s@localhost:3306/G53DT?charset=utf8'%password)
        new_added_house.to_sql("Houses",engine,if_exists = 'append',index_label = "listing_id",index =False)

    #check to-rent property and crawling new property
    os.system("python rentcheck_regular.py 1>rentcheckoutput 2>rentcheckerror")

    time.sleep(60)

    engine =create_engine('mysql+pymysql://root:%s@localhost:3306/G53DT?charset=utf8'%password)
    #Update area information
    area_pipe = AreaPipeline(config)
    #process the area and write the area to database
    area_df = area_pipe.area_process()
    area_df.to_sql(area_pipe.database_name,engine,if_exists = 'replace')

    #switch whole area scale eg. from small zone SW3 SW4 to big zone: SW E N
    area_pipe.switch_area(config)

    #process the area and write the area to database
    area_df = area_pipe.area_process()
    area_df.to_sql(area_pipe.database_name,engine,if_exists = 'replace')

    time.sleep(28800)    


