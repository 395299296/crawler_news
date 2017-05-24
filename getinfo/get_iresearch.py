from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pyvirtualdisplay import Display
from collections import OrderedDict
from common import config
from common import data
import os
import time
import json
import codecs
import datetime
import logging

home_page = 'http://www.iresearch.cn/'
parser = 'html5lib'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
)

news_dict = {}
# driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)
driver = None
db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
logger = logging.getLogger('iresearch')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_page(page):
    logger.info("start get page:%s", page)
    global driver
    with Display(backend="xvfb", size=(1440, 900)):
        driver = webdriver.Firefox()
        driver.maximize_window()
        driver.get(page)
        logger.info("end get page:%s", page)
        js = "var q=document.body.scrollTop=100000"
        driver.execute_script(js)
        time.sleep(3)

def parse_page(index=0):
    news_ele = driver.find_element_by_id('htm_box')
    news_ele = news_ele.find_elements_by_xpath('li/div')
    for x in news_ele:
        try:
            content_ele = x.find_element_by_class_name('txt')
            title_ele = content_ele.find_element_by_xpath('h3/a')
            title = title_ele.text
            if not title or title in news_dict: continue
            logger.info(title)
            url = title_ele.get_attribute("href")
            detail_ele = content_ele.find_element_by_xpath('p')
            info_ele = content_ele.find_element_by_css_selector('.foot.f-cb')
            time_ele = info_ele.find_element_by_css_selector('.time.f-fr')
            time_ele = time_ele.find_element_by_xpath('span')
            keywords_ele = info_ele.find_element_by_css_selector('.link.f-fl')
            keywords_ele = keywords_ele.find_elements_by_xpath('a')
            content = detail_ele.text
            dt = time_ele.text
            keywords = []
            for y in keywords_ele:
                keywords.append(y.text.strip())

            item_data = data.news_item.copy()
            item_data['source'] = '艾瑞'
            item_data['title'] = title
            item_data['url'] = url
            item_data['keywords'] = ','.join(keywords)
            item_data['content'] = content
            item_data['datetime'] = dt
            item_data['eventtime'] = int(time.time())
            print(item_data)
            return
            db.save_item(item_data)
            news_dict[title] = item_data
        except Exception as e:
            print(e)

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
    driver.quit()
