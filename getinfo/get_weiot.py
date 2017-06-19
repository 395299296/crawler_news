from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('wqpc_wechat_list')
        news_ele = news_ele.find_elements_by_xpath('ul/li')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        content_ele = ele.find_element_by_xpath('a')
        url = content_ele.get_attribute("href")
        content_ele = content_ele.find_element_by_class_name('wqpc_con')
        title_ele = content_ele.find_element_by_xpath('h3')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        content_ele = content_ele.find_element_by_xpath('p')
        time_ele = ele.find_element_by_class_name('wqpc_info')
        time_ele = time_ele.find_elements_by_xpath('span')[1]
        content = content_ele.text
        dt = time_ele.text + datetime.datetime.now().strftime(' %H:%M')

        item_data = self.item.copy()
        item_data['source'] = '威腾网'
        item_data['title'] = title
        item_data['url'] = url
        item_data['catalog'] = '人工智能'
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('weiot', 'http://www.weiot.net/articlelist-7-0-1.html').start()
