import os
import sys
import time
os.system("python extractor.py")
time.sleep(1)
os.system("python classify_region.py sale_extracted.json sale")
os.system("python classify_region.py rent_extracted.json rent")
