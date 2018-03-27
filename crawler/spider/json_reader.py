import json

def json_read(path,filename):
    dict_list = []
    try:
        with open(path+filename,"rb") as f:
            for item in f:
                dict_object = json.loads(item)
                dict_list.append(dict_object)
    except FileNotFoundError as e:
        return [[]]
    return dict_list

