import json
f =open('../zoopla_on_sale.json','r')
d = json.loads(f.readline())
print (d) 
print (type(d))
print (d['title'])
