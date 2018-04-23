import os
import time
i=0

while i <1:
    os.system("scrapy crawl rentspider")
    time_local = time.localtime()
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
    print("Checking Old rent is Done!%s"%dt)
    i+=1
    time.sleep(10800)
os.system("scrapy crawl zoopla_to_rent")
