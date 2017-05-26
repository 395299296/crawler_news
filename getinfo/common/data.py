from collections import OrderedDict
from bson.objectid import ObjectId
import pymongo

news_item = OrderedDict([('source',''), ('title',''), ('url',''), ('content',''), ('datetime','')])

'''
存放数据库
'''
class MongoPipeline(object):

    collection_name = 'items'

    def __init__(self, mongo_uri, mongo_db, mongo_user=None, mongo_pass=None):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        if mongo_user and mongo_pass:
            self.db.authenticate(mongo_user, mongo_pass)

    def close(self):
        self.client.close()

    def save_item(self, item):
        item['_id'] = str(ObjectId())
        self.db[self.collection_name].insert(dict(item))
        return item

    def find_all(self):
        return self.db[self.collection_name].find()

    def find_by_date(self, dt):
        return self.db[self.collection_name].find({"eventtime": {"$gt": dt}})