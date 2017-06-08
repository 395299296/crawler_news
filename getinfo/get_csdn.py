from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_elements_by_class_name('exp_list')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        title_ele = ele.find_element_by_xpath('dt/a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        detail_ele = ele.find_element_by_xpath('dt/p')
        info_ele = ele.find_element_by_xpath('dd')
        source_ele = info_ele.find_element_by_class_name('exp_list_l')
        time_ele = info_ele.find_element_by_xpath('div[@class="exp_list_r"]/span')
        date_time = datetime.datetime.strptime(time_ele.text,'%Y-%m-%d %H:%M:%S')
        dt = date_time.strftime('%Y-%m-%d %H:%M')

        item_data = self.item.copy()
        item_data['source'] = source_ele.text
        item_data['title'] = title
        item_data['url'] = url
        item_data['catalog'] = '人工智能'
        item_data['content'] = detail_ele.text
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('csdn', 'http://blog.csdn.net/wemedia.html?category=2').start()
