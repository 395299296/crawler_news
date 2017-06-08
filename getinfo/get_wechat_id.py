from collections import OrderedDict
from browser import Firefox
from common import config
import os, time, datetime
import json, codecs

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self, index=1):
        time.sleep(3)
        news_ele = self.driver.find_element_by_class_name('news-box')
        news_ele = news_ele.find_elements_by_xpath('ul/li')
        for x in news_ele:
            info_ele = x.find_element_by_xpath('.//p[@class="info"]')
            id_ele = info_ele.find_element_by_tag_name('label')
            wid = id_ele.text
            if wid in self.items_dict: continue            
            title_ele = x.find_element_by_xpath('.//p[@class="tit"]/a')
            url = title_ele.get_attribute("href")
            title = title_ele.text
            content = ''
            source = ''
            article = ''
            dt = ''
            content_ele = x.find_elements_by_xpath('dl')
            for y in content_ele:
                dt_ele = y.find_element_by_xpath('dt')
                dd_ele = y.find_element_by_xpath('dd')
                if '功能介绍' in dt_ele.text:
                    content = dd_ele.text
                elif '微信认证' in dt_ele.text:
                    source = dd_ele.text
                elif '最近文章' in dt_ele.text:
                    article_ele = dd_ele.find_element_by_xpath('a')
                    time_ele = dd_ele.find_element_by_xpath('span')
                    article = article_ele.text
                    dt = time_ele.text
            if '分钟' in dt or '小时' in dt:
                dt = datetime.datetime.now().strftime('%Y-%m-%d')
            self.logger.info(title)
            item_data = self.item.copy()
            item_data['title'] = title
            item_data['wid'] = wid
            item_data['url'] = url
            item_data['active'] = 0
            item_data['content'] = content
            item_data['source'] = source
            item_data['article'] = article
            item_data['datetime'] = dt
            self.write_item(item_data, 'wechat_id.txt')

        self.load_more(index)

    def load_more(self, index=1):
        try:
            #获取更多
            more_ele = self.driver.find_element_by_id('sogou_next')
            more_ele.click()
            index = index + 1
            self.logger.info('load page... ... ... ... ... ... ... ...%d', index)
            self.parse_page(index)
        except Exception as e:
            self.logger.info(e)

    def find_info(self):
        """read history data from local file"""
        self.items_dict = {}
        if not os.path.exists(config.output_path):
            os.makedirs(config.output_path)

        output_file = os.path.join(config.output_path, 'wechat_id.txt')
        if not os.path.exists(output_file):
            return None

        with codecs.open(output_file, 'r', encoding='utf-8') as f:
            txt = f.read()
            if not txt:
                return None
            lines = txt.split('\n\n')
            for x in lines:
                if not x: continue
                item_obj = json.loads(x, object_pairs_hook=OrderedDict)
                self.items_dict[item_obj['wid']] = item_obj


if __name__ == '__main__':
    Spider('wechat', 'http://weixin.sogou.com/weixin?query=机器之心').start()
