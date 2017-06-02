from browser import Firefox
import datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_elements_by_class_name('feed-card-item')
        for x in news_ele:
            title_ele = x.find_element_by_xpath('h2/a')
            time_ele = x.find_element_by_xpath('.//div[@class="feed-card-time"]')
            title = title_ele.text
            dt = time_ele.text
            if not title or title in self.items_dict: continue
            if '今天' not in dt: continue
            self.logger.info(title)
            url = title_ele.get_attribute("href")
            content_ele = x.find_element_by_xpath('.//div[@class="feed-card-txt"]')
            detail_ele = content_ele.find_element_by_class_name('feed-card-txt-summary')
            keywords_ele = x.find_elements_by_xpath('.//div[@class="feed-card-tags"]/span/a')
            content = detail_ele.text
            keywords = []
            for y in keywords_ele:
                keywords.append(y.text.strip())

            item_data = self.item.copy()
            item_data['source'] = '新浪科技'
            item_data['title'] = title
            item_data['url'] = url
            item_data['keywords'] = ','.join(keywords)
            item_data['content'] = content
            item_data['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d ') + dt.replace('今天', '')
            self.save_item(item_data)

## Spider('sina', 'http://tech.sina.com.cn/internet/').start()