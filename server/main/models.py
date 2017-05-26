from app.config import config
from app import db
import os

item_list = []
item_dict = {}
keywords = []
lastdate = None

class Items(db.Document):
    source = db.StringField(required=True)
    title = db.StringField(required=True)
    url = db.StringField(required=True)
    content = db.StringField(max_length=255, required=True)
    datetime = db.StringField(required=True)
    wid = db.StringField(required=False)
    catalog = db.StringField(required=False)
    keywords = db.StringField(required=False)
    eventtime = db.IntField(required=False)

def get_keywords():
    config_name = os.getenv('config') or 'default'
    data_file = os.path.join(config[config_name].DATA_PATH, 'keywords.txt')
    with open(data_file, 'r', encoding='utf-8') as f:
        keywords = f.read().split('\n')
        return keywords

def load_data():
    global item_list
    global item_dict
    global keywords
    global lastdate
    data_list = Items.objects.all().order_by('-datetime')
    keywords = get_keywords()
    for x in data_list:
        if check_data(x):
            item_list.append(x)
            item_dict[x.id] = x
            if lastdate == None:
                lastdate = x.datetime

    if lastdate == None:
        lastdate = 0

def check_data(item):
    if item.id in item_dict:
        return False

    if item.source == '微信公众号':
        return True

    if 'catalog' in item:
        if item.catalog in keywords:
            return True
    elif 'keywords' in item:
        tmplist = item.keywords.split(',')
        for x in tmplist:
            if x in keywords:
                return True
    else:
        for x in keywords:
            if x.strip() == '': continue
            if x in item.title:
                return True

        for x in keywords:
            if x.strip() == '': continue
            if x in item.content:
                return True

    return False

def get_data(index=0):
    count = 20
    start = index * count
    end = (index + 1) * count
    return item_list[start:end]

def add_data():
    global lastdate
    if lastdate == None:
        return
    count = 0
    data_list = Items.objects(datetime__gte=lastdate)
    for x in data_list:
        if check_data(x):
            item_list.insert(0, x)
            item_dict[x.id] = x
            if x.datetime >= lastdate:
                lastdate = x.datetime
            count += 1
    print("add data:", lastdate, len(data_list), count)