from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('list_jc')
        news_ele = news_ele.find_elements_by_xpath('li')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        title_ele = ele.find_element_by_xpath('a')
        title = title_ele.get_attribute("title")
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        content_ele = ele.find_element_by_class_name('cn')
        time_ele = ele.find_element_by_class_name('xx')
        time_ele = time_ele.find_element_by_class_name('rq')
        content = content_ele.text
        dt = time_ele.text + datetime.datetime.now().strftime(' %H:%M')

        item_data = self.item.copy()
        item_data['source'] = '人工智能实验室'
        item_data['title'] = title
        item_data['url'] = url
        item_data['catalog'] = '人工智能'
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('ailab', 'http://ai.ailab.cn/').start()
