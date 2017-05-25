from collections import OrderedDict
from common import config
import os, json, time, datetime
import codecs
import csv

items_dict = {}

def read_info(filename):
    """read history data from local file"""
    output_file = os.path.join(config.output_path, filename)
    if not os.path.exists(output_file):
        return None

    with codecs.open(output_file, 'r', encoding='utf-8') as f:
        txt = f.read()
        if not txt:
            return None
        lines = txt.split('\n\n')
        for x in lines:
            if not x: continue
            item_obj = json.loads(x, object_pairs_hook=OrderedDict)
            items_dict[item_obj['wid']] = item_obj

def write_csv(filename, columns, dict_data):
    if not os.path.exists(config.output_path):
        os.makedirs(config.output_path)
    with open(os.path.join(config.output_path, filename), 'w', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for x in dict_data:
            writer.writerow(dict_data[x])

def write_item(items_json, filename):
    """write data to local file"""
    if not os.path.exists(config.output_path):
        os.makedirs(config.output_path)
    txt = json.dumps(items_json, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(config.output_path, filename), 'a', encoding='utf-8') as f:
        f.write(txt)
        f.write('\n\n')


if __name__ == '__main__':
    read_info('wechat_id.txt')
    # columns = ['wid','title','url', 'content', 'source', 'article', 'datetime', 'active']
    # write_csv('wechat_id.csv', columns, items_dict)
    item_list = []
    for x in items_dict:
        item = items_dict[x]
        if '天' in item['datetime']:
            item['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d')
        if item['datetime']:
            date_time = datetime.datetime.strptime(item['datetime'],'%Y-%m-%d')
            item['datetime'] = date_time.strftime('%Y-%m-%d')
            item['timestamp'] = time.mktime(date_time.timetuple())
        else:
            item['timestamp'] = 0
        item_list.append(item)

    item_list = sorted(item_list, key=lambda x : x['timestamp'], reverse=True)
    for x in item_list:
        write_item(x, 'wechat_id_sorted.txt')
