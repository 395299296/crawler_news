from common import config
from common import data

db_local = data.MongoPipeline(config.mongo_uri, config.mongo_database)
db_remote = data.MongoPipeline("123.207.25.160", config.mongo_database, config.mongo_user, config.mongo_pass)

item_list = db_local.find_all()
for i, x in enumerate(item_list):
    try:
        print('save item:', i, x['title'])
    except Exception as e:
        print(e)
    db_remote.save_item(x)
