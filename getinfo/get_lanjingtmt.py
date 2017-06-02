from browser import Firefox
import time, datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('in-main-l')
        news_ele = news_ele.find_elements_by_xpath('dl/dd')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        title_ele = ele.find_element_by_xpath('h2/a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        content_ele = ele.find_elements_by_xpath('p')
        time_ele = content_ele[0]
        content = content_ele[1].text
        dt = time_ele.text
        n = dt.index(' ')
        dt = dt[n+1:]
        if '分钟' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(minutes=int(dt.split('分钟')[0]))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '小时' in dt:
            date_time = datetime.datetime.now() - datetime.timedelta(hours=int(dt.split('小时')[0]))
            dt = date_time.strftime('%Y-%m-%d %H:%M')
        elif '今天' in dt:
            dt = datetime.datetime.now().strftime('%Y-%m-%d ') + dt.split('今天')[1]
        else:
            date_time = datetime.datetime.strptime(dt,'%m月%d日 %H:%M')
            dt = datetime.datetime.now().strftime('%Y-') + date_time.strftime('%m-%d %H:%M')

        item_data = self.item.copy()
        item_data['source'] = '蓝鲸TMT'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ''
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

## Spider('lanjingtmt', 'http://www.lanjingtmt.com/').start()
