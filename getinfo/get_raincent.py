from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('col-left')
        news_ele = news_ele.find_elements_by_xpath('ul/li')
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
        content_ele = ele.find_element_by_xpath('p')
        time_ele = ele.find_element_by_xpath('div/span')
        dt = time_ele.text

        item_data = self.item.copy()
        item_data['source'] = '网络大数据'
        item_data['title'] = title
        item_data['url'] = url
        item_data['catalog'] = '大数据'
        item_data['content'] = content_ele.text
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('raincent', 'http://www.raincent.com/list-85-1.html').start()
