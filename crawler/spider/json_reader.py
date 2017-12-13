import json

def json_read(path,filename):
    dict_list = []
    with open(path+filename,"r") as f:
        for item in f:
            dict_object = json.loads(item)
            dict_list.append(dict_object)
    return dict_list 

