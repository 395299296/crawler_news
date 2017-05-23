from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from collections import OrderedDict
from lxml import etree
from common import config
from common import data
import os
import time
import json
import codecs
import datetime
import requests
import logging

home_page = 'http://next.ithome.com/ai'
parser = 'html5lib'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
)

news_dict = {}
driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)
db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
logger = logging.getLogger('ithome')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_page(page):
    logger.info("start get page:%s", page)
    driver.get(page)
    logger.info("end get page:%s", page)
    js = "var q=document.body.scrollTop=100000"
    driver.execute_script(js)
    time.sleep(3)

def parse_page(index=0):
    news_ele = driver.find_elements_by_xpath('//ul[@class="ulcl"]/li')
    for x in news_ele:
        try:
            title_ele = x.find_element_by_xpath('div/h2/a')
            time_ele = x.find_element_by_xpath('div/h2/span')
            title = title_ele.text
            dt = time_ele.text
            if not title or title in news_dict: continue
            if '今日' not in dt: continue
            logger.info(title)
            url = title_ele.get_attribute("href")
            content_ele = x.find_element_by_xpath('div/div/p')
            keywords_ele = x.find_elements_by_xpath('div/span/a')
            content = content_ele.text
            dt = dt.split(' ')[1]
            keywords = []
            for x in keywords_ele:
                text = x.text.strip()
                if text not in ['', ',', '，']:
                    keywords.append(text)

            item_data = data.news_item.copy()
            item_data['source'] = 'IT之家'
            item_data['title'] = title
            item_data['url'] = url
            item_data['keywords'] = ','.join(keywords)
            item_data['content'] = content
            item_data['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d ') + dt
            item_data['eventtime'] = int(time.time())
            db.save_item(item_data)
            news_dict[title] = item_data
        except Exception as e:
            pass

def find_info():
    """ 查找信息 """
    days = datetime.timedelta(days=3)
    startdate = datetime.datetime.now() - days
    startdate = startdate.strftime('%Y-%m-%d %H:%M')
    items = db.find_by_date(startdate)
    for x in items:
        news_dict[x['title']] = x

if __name__ == '__main__':
    if not os.path.exists(config.output_path):
        os.makedirs(config.output_path)
    find_info()
    #访问目标网页地址
    get_page(home_page)
    parse_page()

    db.close()
    driver.close()
