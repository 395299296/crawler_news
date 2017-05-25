from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium import webdriver
from collections import OrderedDict
from browser import Firefox
from common import config
import os, json, time, datetime
import codecs

item_list = []

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
        self.driver.set_page_load_timeout(60)
        self.driver.set_script_timeout(30)

    def parse_page(self, index=0):
        cookies = self.driver.get_cookies()
        print(cookies)
        answer = int(input("input a number: "))
        new_cookies = [{'path': '/', 'httpOnly': False, 'expiry': None, 'value': 'FB89F03BE2E4B2B7105713E5E26B4AB6', 'domain': '.sogou.com', 'name': 'SNUID', 'secure': False}, {'path': '/', 'httpOnly': False, 'expiry': None, 'value': 'success', 'domain': '.weixin.sogou.com', 'name': 'seccodeRight', 'secure': False}, {'path': '/', 'httpOnly': False, 'expiry': None, 'value': '1|Thu, 25 May 2017 10:50:00 GMT', 'domain': '.weixin.sogou.com', 'name': 'successCount', 'secure': False}, {'path': '/', 'httpOnly': False, 'expiry': None, 'value': '1', 'domain': '.weixin.sogou.com', 'name': 'refresh', 'secure': False}, {'path': '/', 'httpOnly': False, 'expiry': None, 'value': 'aaaVxa_Be9N1ag40UGFWv', 'domain': 'weixin.sogou.com', 'name': 'JSESSIONID', 'secure': False}]
        for x in new_cookies:
            self.driver.add_cookie(x)
        self.driver.refresh()
        answer = int(input("input a number: "))
        cookies = self.driver.get_cookies()
        print(cookies)
        answer = int(input("input a number: "))
        news_ele = self.driver.find_element_by_class_name('news-box')
        news_ele = news_ele.find_elements_by_xpath('ul/li')
        title_ele = news_ele[0].find_element_by_xpath('.//p[@class="tit"]/a')
        url = title_ele.get_attribute("href")
        self.get_page(url)
        self.parse_detail_page(index)

    def parse_detail_page(self, index=0):
        self.logger.info('%s:%d/%d', item_list[index]['title'], index+1, len(item_list))
        answer = int(input("input a number: "))
        news_ele = self.driver.find_element_by_id('history')
        news_ele = news_ele.find_elements_by_class_name('weui_msg_card')
        for x in news_ele:
            info_ele = x.find_element_by_xpath('.//div[@class="weui_media_bd"]')
            title_ele = info_ele.find_element_by_tag_name('h4')
            title = title_ele.text
            if not title or title in self.items_dict: continue
            self.logger.info(title)
            url = title_ele.get_attribute("hrefs")
            content_ele = info_ele.find_element_by_class_name('weui_media_desc')
            time_ele = info_ele.find_element_by_class_name('weui_media_extra_info')
            dt = time_ele.text
            date_time = datetime.datetime.strptime(dt,'%Y年%m月%d日')
            dt = date_time.strftime('%Y-%m-%d %H:%M')
            item_data = self.item.copy()
            item_data['source'] = '微信公众号'
            item_data['title'] = title
            item_data['url'] = url
            item_data['keywords'] = item_list[index]['source']
            item_data['content'] = content_ele.text
            item_data['datetime'] = dt
            print(item_data)
            return
            self.save_item(item_data)

        index = index + 1
        if len(item_list) > index:
            self.get_page('http://weixin.sogou.com/weixin?query=%s' % item_list[index]['wid'])
            self.parse_page(index)


def read_info(filename):
    """read history data from local file"""
    global item_list
    input_file = os.path.join(config.output_path, filename)
    if not os.path.exists(input_file):
        return None

    tmp_dict = {}
    with codecs.open(input_file, 'r', encoding='utf-8') as f:
        txt = f.read()
        if not txt:
            return None
        lines = txt.split('\n\n')
        for x in lines:
            if not x: continue
            item_obj = json.loads(x, object_pairs_hook=OrderedDict)
            tmp_dict[item_obj['wid']] = item_obj
    for x in tmp_dict:
        item_list.append(tmp_dict[x])

    item_list = sorted(item_list, key=lambda x : x['datetime'], reverse=True)

if __name__ == '__main__':
    read_info('wechat_id_handled.txt')
    Spider('wechat', 'http://weixin.sogou.com/weixin?query=%s' % item_list[0]['wid']).start()
