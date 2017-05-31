from collections import defaultdict
from common import config
from common import data
import os

db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
item_list = db.find_all()
source_dict = defaultdict(lambda: 0)
for x in item_list:
    if x['source'] == '微信公众号': continue
    tmp_list = x['source'].split('/')
    for y in tmp_list:
        source_dict[y.strip()] += 1

source_list = source_dict.items()
source_list = sorted(source_list, key=lambda x : x[1], reverse=True)

if not os.path.exists(config.output_path):
        os.makedirs(config.output_path)
with open(os.path.join(config.output_path, 'sources.txt'), 'w', encoding='utf-8') as f:
    source_str = ''
    for x in source_list:
        source_str += x[0] + '\t' + str(x[1]) + '\n'
    f.write(source_str)

db.close()