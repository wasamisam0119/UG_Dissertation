import os
import time
i=0

while i <1:
    os.system("scrapy crawl salespider")
    time_local = time.localtime()
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
    print("Checking Old sale is Done!%s"%dt)
    i+=1
    time.sleep(10800)
os.system("scrapy crawl zoopla_on_sale")
