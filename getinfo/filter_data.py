from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from collections import OrderedDict
from browser import Firefox
from common import config
import os, json, time, datetime
import codecs

item_list = []
items_dict = {}

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)

    def init_profile(self):
        """init the Firefox profile object"""
        self.profile = FirefoxProfile()

    def init_driver(self):
        """init web driver"""
        ## Set the modified profile while creating the browser object
        self.driver = webdriver.Firefox(self.profile)
        self.driver.set_page_load_timeout(30)  
        self.driver.set_script_timeout(30)

    def get_page(self, page):
        """browse target page"""
        self.logger.info("start get page:%s", page)
        try:
            self.driver.get(page)
        except Exception as e:
            pass
        self.logger.info("end get page:%s", page)
          
    def parse_page(self, index=0):
        global item_list
        """parse current page source"""
        if len(item_list) == 0:
            item_list = list(self.items_dict.items())
        else:
            answer = int(input("is save: "))
            if answer == 1:
                self.write_item(item_list[index][1], 'wechat_id_handled.txt')
            items_dict[item_list[index][1]['title']] = item_list[index][1]
        for x in range(0,len(item_list)):
            if item_list[x][1]['title'] not in items_dict:
                index = x
                break
        self.get_page(item_list[index][1]['url'])
        self.parse_page(index)

    def find_info(self):
        """read history data from local file"""
        self.read_info('wechat_id_sorted.txt')
        

def read_info(filename):
    """read history data from local file"""
    global items_dict
    input_file = os.path.join(config.output_path, filename)
    if not os.path.exists(input_file):
        return None

    with codecs.open(input_file, 'r', encoding='utf-8') as f:
        txt = f.read()
        if not txt:
            return None
        lines = txt.split('\n\n')
        for x in lines:
            if not x: continue
            item_obj = json.loads(x, object_pairs_hook=OrderedDict)
            items_dict[item_obj['title']] = item_obj

if __name__ == '__main__':
    read_info('wechat_id_handled.txt')
    Spider('wechat', '').start()