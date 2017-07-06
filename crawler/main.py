import time
import os

while True:
    os.system("scrapy crawl zoopla_on_sale")
    time.sleep(3600)
