from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from collections import OrderedDict
from common import config
from common import data
import os
import time
import json
import codecs
import datetime
import logging

home_page = 'http://36kr.com/'
parser = 'html5lib'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
)

news_dict = {}
driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)
db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
logger = logging.getLogger('36kr')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_page(page):
    logger.info("start get page:%s", page)
    driver.get(page)
    logger.info("end get page:%s", page)
    js = "var q=document.body.scrollTop=100000"
    driver.execute_script(js)
    time.sleep(3)

def parse_page(index=0):
    a = driver.find_elements_by_class_name('abstract')
    print(len(a))
    for x in a:
        print(dir(x))
        exit()
    news_ele = driver.find_element_by_class_name('kr_article_list')
    news_ele = news_ele.find_elements_by_xpath('div/ul/li')
    for x in news_ele:
        content_ele = x.find_element_by_xpath('div/a')
        url = content_ele.get_attribute("href")
        content_ele = content_ele.find_element_by_class_name('intro')
        title_ele = content_ele.find_element_by_tag_name('h3')
        title = title_ele.text
        if not title or title in news_dict: continue
        logger.info(title)
        detail_ele = content_ele.find_element_by_class_name('abstract')
        info_ele = x.find_element_by_xpath('div/div')
        time_ele = info_ele.find_elements_by_xpath('.//div[@class="time-div"]/span')[0]
        keywords_ele = info_ele.find_elements_by_xpath('div[@class="tags-list"]/span')
        content = detail_ele.text
        dt = time_ele.get_attribute("title")
        keywords = []
        for y in keywords_ele:
            keywords.append(y.text.strip())

        item_data = data.news_item.copy()
        item_data['source'] = '36氪'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ','.join(keywords)
        item_data['content'] = content
        item_data['datetime'] = dt
        item_data['eventtime'] = int(time.time())
        print(item_data)
        exit()
        db.save_item(item_data)
        news_dict[title] = item_data

def find_info():
    """ 查找信息 """
    startdate = int(time.time()) - 3600 * 24 * 3
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
