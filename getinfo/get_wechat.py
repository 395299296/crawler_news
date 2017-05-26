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

    def find_info(self, days=3):
        """find history data in db"""
        super(Firefox, self).find_info(1)

    def parse_page(self, index=-1):
        if index == -1:
            for i, x in enumerate(item_list):
                for y in self.items_dict:
                    if self.items_dict[y]['source'] == '微信公众号' and x['title'] == self.items_dict[y]['keywords']:
                        break
                else:
                    index = i
                    self.get_page('http://weixin.sogou.com/weixin?query=%s' % x['wid'])
                    break
            else:
                self.logger.info('find not getable account')
                return
        self.logger.info('%s:%d/%d', item_list[index]['title'], index+1, len(item_list))
        try:
            news_ele = self.driver.find_element_by_class_name('news-box')    
        except Exception as e:
            answer = input("input verify code: ")
            if answer == 'exit()': return
            cookies = self.driver.get_cookies()
            print(cookies)
            self.driver.delete_all_cookies()
            new_cookies = [{'httpOnly': False, 'value': '8|1495769364|v1', 'domain': 'weixin.sogou.com', 'secure': False, 'name': 'ABTEST', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': 'C8BAC30BD2D782B520725F7CD27EAE38', 'domain': '.sogou.com', 'secure': False, 'name': 'SNUID', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': 'CN4403', 'domain': '.sogou.com', 'secure': False, 'name': 'IPLOC', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': '1A6B11DA771A910A000000005927A114', 'domain': '.weixin.sogou.com', 'secure': False, 'name': 'SUID', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': 'aaakmrSdQn-eY_tEYIFWv', 'domain': 'weixin.sogou.com', 'secure': False, 'name': 'JSESSIONID', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': '1A6B11DA3020910A000000005927A114', 'domain': '.sogou.com', 'secure': False, 'name': 'SUID', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': '00AB734EDA116B1A5927A11575694165', 'domain': '.sogou.com', 'secure': False, 'name': 'SUV', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': 'p0hc3jvqk4f0pcgjqjghv9sg01', 'domain': 'weixin.sogou.com', 'secure': False, 'name': 'PHPSESSID', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': 'C8BAC30BD2D782B520725F7CD27EAE38', 'domain': '.sogou.com', 'secure': False, 'name': 'SUIR', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': 'success', 'domain': '.weixin.sogou.com', 'secure': False, 'name': 'seccodeRight', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': '1|Fri, 26 May 2017 03:36:25 GMT', 'domain': '.weixin.sogou.com', 'secure': False, 'name': 'successCount', 'path': '/', 'expiry': None}, {'httpOnly': False, 'value': '1', 'domain': '.weixin.sogou.com', 'secure': False, 'name': 'refresh', 'path': '/', 'expiry': None}]
            for x in new_cookies:
                self.driver.add_cookie({'name':x['name'], 'value':x['value']})
            self.get_page(self.page)
            self.parse_page(index)
            return

        news_ele = news_ele.find_elements_by_xpath('ul/li')
        title_ele = news_ele[0].find_element_by_xpath('.//p[@class="tit"]/a')
        url = title_ele.get_attribute("href")
        self.get_page(url)
        self.parse_detail_page(index)

    def parse_detail_page(self, index=0):
        try:
            news_ele = self.driver.find_element_by_id('history')
        except Exception as e:
            answer = input("input verify code: ")
            if answer == 'exit()': return
            input_ele = self.driver.find_element_by_id('input')
            input_ele.send_keys(answer)
            bt_ele = self.driver.find_element_by_id('bt')
            bt_ele.click()
            time.sleep(3)
            # self.get_page(self.page)
            self.parse_detail_page(index)
            return
            
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
            item_data['url'] = 'http://mp.weixin.qq.com' + url
            item_data['wid'] = item_list[index]['wid']
            item_data['keywords'] = item_list[index]['title']
            item_data['content'] = content_ele.text
            item_data['datetime'] = dt
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

    item_list = sorted(item_list, key=lambda x : (x['datetime'], x['wid']), reverse=True)

if __name__ == '__main__':
    read_info('wechat_id_handled.txt')
    Spider('wechat', '').start()
