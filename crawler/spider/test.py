import requests
import json
"""
f =open('../zoopla_on_sale.json','r')
d = json.loads(f.readline())
print (d) 
print (d['title'])
"""
content = requests.get("http://p.3.cn/prices/get?skuid=J_10037872")
d = json.loads(content.text)
print (d)
print (type(d))

