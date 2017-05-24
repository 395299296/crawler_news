from browser import Firefox

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_id('news')
        news_ele = news_ele.find_elements_by_class_name('Q-tpList')
        item_list = []
        for x in news_ele:
            title_ele = x.find_element_by_tag_name('h3')
            title_ele = title_ele.find_element_by_tag_name('a')
            title = title_ele.text
            if not title or title in self.items_dict: continue
            self.logger.info(title)
            url = title_ele.get_attribute("href")

            item_data = self.item.copy()
            item_data['title'] = title
            item_data['url'] = url
            item_list.append(item_data)

        for x in item_list:
            self.get_page(x['url'])
            x['catalog'], x['source'], x['datetime'], x['content'] = self.parse_detail_page()

        for x in item_list:
            self.save_item(x)

    def parse_detail_page(self):
        """ 获取详情页信息 """
        info_ele = self.driver.find_element_by_class_name('a_Info')
        catalog_ele = info_ele.find_element_by_xpath('span[@class="a_catalog"]/a')
        try:
            source_ele = info_ele.find_element_by_xpath('span[@class="a_source"]/a')
        except Exception as e:
            source_ele = info_ele.find_element_by_xpath('span[@class="a_source"]')
        time_ele = info_ele.find_element_by_xpath('span[@class="a_time"]')
        content_ele = self.driver.find_element_by_id('Cnt-Main-Article-QQ')
        content_ele = content_ele.find_elements_by_xpath('p[@class="text"]')
        content = ''
        for x in content_ele:
            if not x.text: continue
            content += x.text.strip()
            if len(content) >= 64:
                break
        return catalog_ele.text, source_ele.text, time_ele.text, content


Spider('tencent', 'http://tech.qq.com/').start()
