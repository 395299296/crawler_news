from browser import Firefox

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_id('htm_box')
        news_ele = news_ele.find_elements_by_xpath('li/div')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        content_ele = ele.find_element_by_class_name('txt')
        title_ele = content_ele.find_element_by_xpath('h3/a')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        url = title_ele.get_attribute("href")
        detail_ele = content_ele.find_element_by_xpath('p')
        info_ele = content_ele.find_element_by_css_selector('.foot.f-cb')
        time_ele = info_ele.find_element_by_css_selector('.time.f-fr')
        time_ele = time_ele.find_element_by_xpath('span')
        keywords_ele = info_ele.find_element_by_css_selector('.link.f-fl')
        keywords_ele = keywords_ele.find_elements_by_xpath('a')
        content = detail_ele.text
        dt = time_ele.text
        keywords = []
        for y in keywords_ele:
            keywords.append(y.text.strip())

        item_data = self.item.copy()
        item_data['source'] = '艾瑞'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ','.join(keywords)
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

## Spider('iresearch', 'http://www.iresearch.cn/').start()