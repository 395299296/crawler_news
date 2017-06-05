from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('mod-info-flow')
        news_ele = news_ele.find_elements_by_css_selector('.mod-b.mod-art')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        content_ele = ele.find_element_by_class_name('mob-ctt')
        title_ele = content_ele.find_element_by_xpath('h2/a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        detail_ele = content_ele.find_element_by_class_name('mob-sub')
        info_ele = content_ele.find_element_by_class_name('mob-author')
        time_ele = info_ele.find_element_by_xpath('.//span[@class="time"]')
        content = detail_ele.text
        dt = time_ele.text
        if '分钟' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(minutes=int(dt.split('分钟')[0]))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '小时' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(hours=int(dt.split('小时')[0]))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '天' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(days=int(dt.split('天')[0]))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        else:
            dt += datetime.datetime.now().strftime(' %H:%M')

        item_data = self.item.copy()
        item_data['source'] = '虎嗅'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = '人工智能'
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('huxiu', 'https://www.huxiu.com/channel/104.html').start()
