from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('article-item-content')
        news_ele = news_ele.find_elements_by_class_name('article-item')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        content_ele = ele.find_element_by_xpath('.//div[@class="article-info-wrapper"]')
        title_ele = content_ele.find_element_by_class_name('article-title')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        detail_ele = content_ele.find_element_by_class_name('article-description')
        time_ele = content_ele.find_element_by_css_selector('.article-time.js-relative-time.dib-middle')
        content = detail_ele.text
        dt = time_ele.get_attribute("title")
        date_time = datetime.datetime.strptime(dt,'%Y-%m-%d %H:%M:%S')
        dt = date_time.strftime('%Y-%m-%d %H:%M')

        item_data = self.item.copy()
        item_data['source'] = '极客公园'
        item_data['title'] = title
        item_data['url'] = 'http://www.geekpark.net/' + url
        item_data['keywords'] = ''
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

Spider('geekpark', 'http://www.geekpark.net/').start()
