from browser import PhantomJS
import time, datetime

class Spider(PhantomJS):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('mod-instantNews')
        news_ele = news_ele.find_elements_by_class_name('item')
        oneday = datetime.timedelta(days=1)
        yesterday = datetime.datetime.now() - oneday
        for x in news_ele:
            title_ele = x.find_element_by_tag_name('h3')
            title_ele = title_ele.find_element_by_tag_name('a')
            title = title_ele.text
            if not title or title in self.items_dict: continue
            self.logger.info(title)
            url = title_ele.get_attribute("href")
            content_ele = x.find_element_by_class_name('content')
            detail_ele = content_ele.find_element_by_class_name('detail')
            msg_ele = content_ele.find_element_by_class_name('msg-bar')
            span_ele = content_ele.find_elements_by_tag_name('span')
            content = detail_ele.text
            source = span_ele[0].text
            dt = span_ele[1].text

            item_data = self.item.copy()
            item_data['source'] = source
            item_data['title'] = title
            item_data['url'] = url
            item_data['content'] = content
            item_data['datetime'] = yesterday.strftime('%Y-%m-%d ') + dt
            self.save_item(item_data)

    def load_more(self):
        try:
            #获取更多
            more_ele = self.driver.find_element_by_id('btn-more')
            more_ele = more_ele.find_element_by_tag_name('a')
            more_ele.click()
            time.sleep(3)
            self.parse_page()
        except Exception as e:
            pass

Spider('baidu', 'http://news.baidu.com/internet/').start()