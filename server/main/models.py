from .app import db

item_list = []

class Items(db.Document):
    source = db.StringField(required=True)
    title = db.StringField(required=True)
    url = db.StringField(required=True)
    content = db.StringField(required=True)
    datetime = db.StringField(required=True)

def load_data():
    global item_list
    item_list = Items.objects.all().order_by('-datetime')

def get_data(index=0):
    count = 20
    start = index * count
    end = (index + 1) * count
    print(len(item_list), start, end)
    return item_list[start:end]