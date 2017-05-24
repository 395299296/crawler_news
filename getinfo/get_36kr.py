from browser import Firefox

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('kr_article_list')
        news_ele = news_ele.find_elements_by_xpath('div/ul/li')
        for x in news_ele:
            try:
                self.parse_ele(x)
            except Exception as e:
                print(e)

    def parse_ele(self, ele):
        content_ele = ele.find_element_by_xpath('div/a')
        url = content_ele.get_attribute("href")
        content_ele = content_ele.find_element_by_class_name('intro')
        title_ele = content_ele.find_element_by_tag_name('h3')
        title = title_ele.text
        if not title or title in self.items_dict: return
        self.logger.info(title)
        detail_ele = content_ele.find_element_by_class_name('abstract')
        info_ele = ele.find_element_by_xpath('div/div')
        time_ele = info_ele.find_elements_by_xpath('.//div[@class="time-div"]/span')[0]
        keywords_ele = info_ele.find_elements_by_xpath('div[@class="tags-list"]/span/a')
        content = detail_ele.text
        dt = time_ele.get_attribute("title")
        keywords = []
        for y in keywords_ele:
            keywords.append(y.text.strip())

        item_data = self.item.copy()
        item_data['source'] = '36氪'
        item_data['title'] = title
        item_data['url'] = url
        item_data['keywords'] = ','.join(keywords)
        item_data['content'] = content
        item_data['datetime'] = dt
        self.save_item(item_data)

Spider('36kr', 'http://36kr.com/').start()
