from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_css_selector('.lph-pageList.index-pageList')
        news_ele = news_ele.find_elements_by_class_name('box')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        content_ele = ele.find_element_by_class_name('word')
        title_ele = content_ele.find_element_by_xpath('h3/a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        detail_ele = content_ele.find_element_by_class_name('des')
        time_ele = content_ele.find_element_by_xpath('.//div[@class="time"]')
        info_ele = content_ele.find_element_by_class_name('tags')
        keywords_ele = info_ele.find_elements_by_xpath('a')
        content = detail_ele.text
        dt = time_ele.text
        if '分钟' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(minutes=int(dt.split('分钟')[0]))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '小时' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(hours=int(dt.split('小时')[0]))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '昨天' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(days=1)
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        else:
            date_time = datetime.datetime.strptime(dt,'%m月%d日 %H:%M')
            dt = datetime.datetime.now().strftime('%Y-') + date_time.strftime('%m-%d %H:%M')
        keywords = []
        for y in keywords_ele:
            keywords.append(y.text.strip())

        item_data = self.item.copy()
        item_data['source'] = '雷锋网'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ','.join(keywords)
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

Spider('leiphone', 'https://www.leiphone.com/').start()
