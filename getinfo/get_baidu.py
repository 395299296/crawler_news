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

home_page = 'http://news.baidu.com/internet/'
parser = 'html5lib'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
)

news_dict = {}
driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)
db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
logger = logging.getLogger('baidu')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_page(page):
    logger.info("start get page:%s", page)
    driver.get(page)
    logger.info("end get page:%s", page)
    js = "var q=document.body.scrollTop=100000"
    driver.execute_script(js)
    time.sleep(3)

def parse_page(index=0):
    news_ele = driver.find_element_by_class_name('mod-instantNews')
    news_ele = news_ele.find_elements_by_class_name('item')
    oneday = datetime.timedelta(days=1)
    yesterday = datetime.datetime.now() - oneday
    for x in news_ele:
        title_ele = x.find_element_by_tag_name('h3')
        title_ele = title_ele.find_element_by_tag_name('a')
        title = title_ele.text
        if not title or title in news_dict: continue
        logger.info(title)
        url = title_ele.get_attribute("href")
        content_ele = x.find_element_by_class_name('content')
        detail_ele = content_ele.find_element_by_class_name('detail')
        msg_ele = content_ele.find_element_by_class_name('msg-bar')
        span_ele = content_ele.find_elements_by_tag_name('span')
        content = detail_ele.text
        source = span_ele[0].text
        dt = span_ele[1].text

        item_data = data.news_item.copy()
        item_data['source'] = source
        item_data['title'] = title
        item_data['url'] = url
        item_data['content'] = content
        item_data['datetime'] = yesterday.strftime('%Y-%m-%d ') + dt
        item_data['eventtime'] = int(time.time())
        # save_news(item_data)
        db.save_item(item_data)
        news_dict[title] = item_data
  
    try:
        #获取更多
        more_ele = driver.find_element_by_id('btn-more')
        more_ele = more_ele.find_element_by_tag_name('a')
        more_ele.click()
        index += 1
        logger.info('-' * 50)
        logger.info("show more... ...%s", index)
        logger.info('-' * 50)
        time.sleep(3)
        parse_page(index)
    except Exception as e:
        pass

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
    startdate = int(time.time()) - 3600 * 24 * 3
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
