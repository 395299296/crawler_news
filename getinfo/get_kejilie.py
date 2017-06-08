from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('am-list')
        news_ele = news_ele.find_elements_by_xpath('li')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        main_ele = ele.find_element_by_css_selector('.am-u-sm-8.am_list_main')
        title_ele = main_ele.find_element_by_xpath('h3/a')
        title = title_ele.get_attribute("title")
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        content_ele = main_ele.find_element_by_css_selector('.am-list-item-text.am_list_item_text')
        time_ele = main_ele.find_element_by_class_name('am_list_author')
        time_ele = time_ele.find_element_by_xpath('span/time')
        content = content_ele.text
        dt = time_ele.get_attribute("title")
        date_time = datetime.datetime.strptime(dt,'%H:%M:%S')
        dt = datetime.datetime.now().strftime('%Y-%m-%d ') + date_time.strftime('%H:%M')

        item_data = self.item.copy()
        item_data['source'] = '科技猎'
        item_data['title'] = title
        item_data['url'] = url
        item_data['catalog'] = '人工智能'
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('kejilie', 'http://www.kejilie.com/channel/rengongzhineng.html').start()
