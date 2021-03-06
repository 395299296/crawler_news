from browser import Firefox
import time, datetime, re

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self, index=-1):
        last_index = index
        news_ele = self.driver.find_elements_by_class_name('timelineItem___1T6m9')
        for i, x in enumerate(news_ele):
            if i < index: continue
            try:
                self.parse_ele(x)
                index = i
            except Exception as e:
                print(e)
        if index >= 100 or last_index == index: return
        print('-'*100, index)
        btn_ele = self.driver.find_element_by_class_name('listButtonFix___2Thj0')
        btn_ele = btn_ele.find_element_by_xpath('button/span')
        btn_ele.click()
        time.sleep(3)
        self.parse_page(index)

    def parse_ele(self, ele):
        title_ele = ele.find_element_by_xpath('h2/a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        content_ele = ele.find_element_by_class_name('summary___2wW8Q')
        content = content_ele.get_attribute("data-clamp-text")
        info_ele = ele.find_element_by_class_name('meta___1ARPK')
        meta = info_ele.text.split(' •')
        source = meta[0]
        dt = meta[1]
        mode = re.compile(r'\d+')
        difftime = mode.findall(dt)[0]
        if '分钟' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(minutes=int(difftime))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '小时' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(hours=int(difftime))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '天' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(days=int(difftime))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        item_data = self.item.copy()
        item_data['source'] = source
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ''
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

if __name__ == '__main__':
    Spider('readhub', 'https://readhub.me/news').start()
