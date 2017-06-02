from browser import Firefox
import datetime

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_elements_by_xpath('//ul[@class="ulcl"]/li')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                pass

    def parse_ele(self, ele):
        title_ele = ele.find_element_by_xpath('div/h2/a')
        time_ele = ele.find_element_by_xpath('div/h2/span')
        title = title_ele.text
        dt = time_ele.text
        if not title or title in self.items_dict: return
        if '今日' not in dt: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        content_ele = ele.find_element_by_xpath('div/div/p')
        keywords_ele = ele.find_elements_by_xpath('div/span/a')
        content = content_ele.text
        dt = dt.split(' ')[1]
        keywords = []
        for ele in keywords_ele:
            text = ele.text.strip()
            if text not in ['', ',', '，']:
                keywords.append(text)

        item_data = self.item.copy()
        item_data['source'] = 'IT之家'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ','.join(keywords)
        item_data['content'] = content
        item_data['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d ') + dt
        self.save_item(item_data)

## Spider('ithome', 'http://next.ithome.com/ai').start()