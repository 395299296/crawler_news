from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('list_leftcont')
        news_ele = news_ele.find_elements_by_xpath('ul/li/table/tbody/tr')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        content_ele = ele.find_elements_by_xpath('td')[1]
        title_ele = content_ele.find_element_by_xpath('h2/a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        detail_ele = content_ele.find_elements_by_xpath('p')
        content = detail_ele[0].text
        dt = detail_ele[1].text.split('：')[1]
        dt = dt + datetime.datetime.now().strftime(' %H:%M')

        item_data = self.item.copy()
        item_data['source'] = '21ic'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = '嵌入式'
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('21ic', 'http://embed.21ic.com/news/technology/').start()
