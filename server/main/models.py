from app.config import config
from app import db
import logging
import os, re
import time, datetime

item_list = []
item_dict = {}
keywords = []
last_time = None
logger = logging.getLogger(__name__)
log_file = os.path.join(os.path.dirname(__file__), '../../log.log')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S', filename=log_file, filemode="a")

class Items(db.Document):
    source = db.StringField(required=True)
    title = db.StringField(required=True)
    url = db.StringField(required=True)
    content = db.StringField(max_length=255, required=True)
    datetime = db.StringField(required=True)
    showtime = db.StringField(required=False)
    wid = db.StringField(required=False)
    catalog = db.StringField(required=False)
    keywords = db.StringField(required=False)
    eventtime = db.FloatField(required=False)

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
    global last_time
    data_list = Items.objects.all()
    keywords = get_keywords()
    count = 0
    for x in data_list:
        if check_data(x):
            item_dict[x.title] = x
            count += 1
        last_time = x.eventtime

    item_list = sorted(item_dict.values(), key=lambda x : x['eventtime'], reverse=True)

    if last_time == None:
        last_time = 0
    logger.info("load data:%s,%s,%s,%s", last_time, len(data_list), count, len(item_list))


def check_data(item):
    if not format_datetime(item):
        return False

    handle_url(item)
    if item.source in ['微信公众号', 'AI研究院']:
        return True

    pattern = re.compile(u'[\u4e00-\u9fa5]+')
    if not pattern.search(item.title):
        return False

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
    global last_time
    count = 20
    start = index * count
    end = (index + 1) * count
    logger.info("get data:%s,%s,%s,%s", last_time, start, end, len(item_list))
    return item_list[start:end]

def add_data():
    global last_time
    global item_list
    if last_time == None:
        return
    count = 0
    data_list = Items.objects(eventtime__gt=last_time)
    for x in data_list:
        if check_data(x):
            item_dict[x.title] = x
            count += 1
        last_time = x.eventtime

    if count > 0:
        item_list = sorted(item_dict.values(), key=lambda x : x['eventtime'], reverse=True)
    logger.info("add data:%s,%s,%s,%s", last_time, len(data_list), count, len(item_list))

def format_datetime(item):
    timestamp = item.eventtime
    if not timestamp:
        return False
    if time.time() - timestamp / 1000 < 365 * 24 * 3600:
        timestamp = timestamp / 1000
    if time.time() - timestamp > 365 * 24 * 3600:
        return False
    date_array = datetime.datetime.fromtimestamp(timestamp)
    item.showtime = date_array.strftime("%Y-%m-%d %H:%M")
    return True

def handle_url(item):
    if item.source == '微信公众号':
        item.url = 'http://weixin.sogou.com/weixin?type=2&query=%s'%item.title.replace('原创', '').replace('，', ' ')
