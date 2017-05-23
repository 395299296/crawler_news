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
import re

home_page = 'http://tech.163.com/smart/'
parser = 'html5lib'
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0"
)

news_dict = {}
driver = webdriver.PhantomJS(executable_path=config.browser_path, desired_capabilities=dcap)
db = data.MongoPipeline(config.mongo_uri, config.mongo_database)
logger = logging.getLogger('163')
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
    infolist = tree.xpath('//div[@class="post_content_main"]')[0]
    dt_ele = infolist.xpath('div[@class="post_time_source"]')[0]
    source_ele = dt_ele.xpath('a[@id="ne_article_source"]')[0]
    contet_ele = infolist.xpath('div[@class="post_body"]')[0]
    contet_ele = contet_ele.xpath('div[@class="post_text"]')[0]
    p = contet_ele.xpath('p')
    pattern = re.compile(r'\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}')
    dt = re.findall(pattern, dt_ele.text)[0]
    content = ''
    for x in p:
        if not x.text: continue
        content += x.text.strip()
        if len(content) >= 64:
            break
    return source_ele.text, dt, content

def parse_page(index=0):
    news_ele = driver.find_element_by_class_name('newsdata_item')
    news_ele = news_ele.find_elements_by_css_selector('.data_row.news_article.clearfix')
    for x in news_ele:
        title_ele = x.find_element_by_xpath('.//div[@class="news_title"]/h3/a')
        title = title_ele.text
        if not title or title in news_dict: continue
        logger.info(title)
        url = title_ele.get_attribute("href")
        try:
            source, dt, content = get_detail_page(url)
        except Exception as e:
            print(e)
            continue

        keywords = []
        keywords_ele = x.find_elements_by_xpath('.//div[@class="keywords"]/a')
        for y in keywords_ele:
            keywords.append(y.text.strip())
        item_data = data.news_item.copy()
        item_data['source'] = source
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ','.join(keywords)
        item_data['content'] = content
        item_data['datetime'] = dt
        item_data['eventtime'] = int(time.time())
        db.save_item(item_data)
        news_dict[title] = item_data

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
