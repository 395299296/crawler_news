from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_id('archive')
        news_ele = news_ele.find_elements_by_class_name('post-meta')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        title_ele = ele.find_element_by_xpath('p')
        dt = title_ele.text.split('\n')[1]
        title_ele = title_ele.find_element_by_xpath('a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        detail_ele = ele.find_element_by_xpath('span/p')
        content = detail_ele.text
        dt = dt.split(' · ')[0] + datetime.datetime.now().strftime(' %H:%M')
        date_time = datetime.datetime.strptime(dt,'%Y/%m/%d %H:%M')
        dt = date_time.strftime('%Y-%m-%d %H:%M')

        item_data = self.item.copy()
        item_data['source'] = '伯乐在线'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = 'IT技术'
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('jobbole', 'http://blog.jobbole.com/category/it-tech/').start()
