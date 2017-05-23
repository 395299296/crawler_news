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

home_page = 'http://tech.qq.com/'
parser = 'html5lib'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
)

news_dict = {}
driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)
db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
logger = logging.getLogger('tencent')
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def get_page(page):
    logger.info("start get page:%s", page)
    driver.get(page)
    logger.info("end get page:%s", page)
    js = "var q=document.body.scrollTop=100000"
    driver.execute_script(js)
    time.sleep(3)

def get_detail_page(page):
    """ 获取详情页信息 """
    r = requests.get(page)
    tree = etree.HTML(r.text)
    infolist = tree.xpath('//div[@class="a_Info"]')[0]
    span1 = infolist.xpath('span[@class="a_catalog"]')[0]
    span2 = infolist.xpath('span[@class="a_source"]')[0]
    span3 = infolist.xpath('span[@class="a_time"]')[0]
    contentlist = tree.xpath('//div[@id="Cnt-Main-Article-QQ"]')[0]
    p = contentlist.xpath('p[@class="text"]')
    content = ''
    for x in p:
        if not x.text: continue
        content += x.text.strip()
        if content != '':
            break
    return span1.text, span2.text, span3.text, content

def parse_page(index=0):
    news_ele = driver.find_element_by_id('news')
    news_ele = news_ele.find_elements_by_class_name('Q-tpList')
    for x in news_ele:
        title_ele = x.find_element_by_tag_name('h3')
        title_ele = title_ele.find_element_by_tag_name('a')
        try:
            title = title_ele.text
            if not title or title in news_dict: continue
            logger.info(title)
            url = title_ele.get_attribute("href")
            catalog, source, dt, content = get_detail_page(url)
        except Exception as e:
            print(e)
            continue

        item_data = data.news_item.copy()
        item_data['source'] = source
        item_data['title'] = title
        item_data['url'] = url
        item_data['catalog'] = catalog
        item_data['content'] = content
        item_data['datetime'] = dt
        item_data['eventtime'] = int(time.time())
        logger.info(item_data)
        exit()
        db.save_item(item_data)
        news_dict[title] = item_data
  
    try:
        #获取更多
        more_ele = driver.find_element_by_id('loadmore')
        if more_ele.text == '更多>>':
            more_ele.click()
            index += 1
            logger.info('-' * 50)
            logger.info("show more... ...%s", index)
            logger.info('-' * 50)
            time.sleep(3)
            parse_page(index)
    except Exception as e:
        raise e

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
