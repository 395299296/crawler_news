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

home_page = 'http://tech.sina.com.cn/internet/'
parser = 'html5lib'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
)

news_dict = {}
driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)
db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
logger = logging.getLogger('sina')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_page(page):
    logger.info("start get page:%s", page)
    driver.get(page)
    logger.info("end get page:%s", page)
    js = "var q=document.body.scrollTop=100000"
    driver.execute_script(js)
    time.sleep(3)

def parse_page(index=0):
    news_ele = driver.find_elements_by_class_name('feed-card-item')
    for x in news_ele:
        title_ele = x.find_element_by_xpath('h2/a')
        time_ele = x.find_element_by_xpath('.//div[@class="feed-card-time"]')
        title = title_ele.text
        dt = time_ele.text
        if not title or title in news_dict: continue
        if '今天' not in dt: continue
        logger.info(title)
        url = title_ele.get_attribute("href")
        content_ele = x.find_element_by_xpath('.//div[@class="feed-card-txt"]')
        detail_ele = content_ele.find_element_by_class_name('feed-card-txt-summary')
        keywords_ele = x.find_elements_by_xpath('.//div[@class="feed-card-tags"]/span/a')
        content = detail_ele.text
        keywords = []
        for y in keywords_ele:
            keywords.append(y.text.strip())

        item_data = data.news_item.copy()
        item_data['source'] = '新浪科技'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ','.join(keywords)
        item_data['content'] = content
        item_data['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d ') + dt.replace('今天', '')
        item_data['eventtime'] = int(time.time())
        db.save_item(item_data)
        news_dict[title] = item_data

def get_info():
    """ 读取信息 """
    output_file = os.path.join(config.output_path, 'baidu.txt')
    if not os.path.exists(output_file):
        return None

    with codecs.open(output_file, 'r', encoding='utf-8') as f:
        txt = f.read()
        if not txt:
            return None
        lines = txt.split('\n\n')
        for x in lines:
            if not x: continue
            news_obj = json.loads(x, object_pairs_hook=OrderedDict)
            news_dict[news_obj['title']] = news_obj

def save_news(news_json):
    """ 保存信息 """
    txt = json.dumps(news_json, ensure_ascii=False, indent=2)
    with codecs.open(os.path.join(config.output_path, 'baidu.txt'), 'a', encoding='utf-8') as f:
        f.write(txt)
        f.write('\n\n')

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
    # get_info()
    find_info()
    #访问目标网页地址
    get_page(home_page)
    parse_page()

    db.close()
    driver.close()
