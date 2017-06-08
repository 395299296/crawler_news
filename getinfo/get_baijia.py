from browser import Firefox

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_id('articleList')
        news_ele = news_ele.find_elements_by_xpath('div')
        item_list = []
        for x in news_ele:
            title_ele = x.find_element_by_class_name('title')
            title_ele = title_ele.find_element_by_tag_name('a')
            title = title_ele.text
            if not title or title in self.items_dict: continue
            self.logger.info(title)
            url = title_ele.get_attribute("href")

            item_data = self.item.copy()
            item_data['title'] = title
            item_data['url'] = url
            item_data['source'] = '百家号'
            item_list.append(item_data)

        for x in item_list:
            self.get_page(x['url'])
            x['datetime'], x['content'] = self.parse_detail_page()

        for x in item_list:
            self.save_item(x)

    def parse_detail_page(self):
        """ 获取详情页信息 """
        article_ele = self.driver.find_element_by_class_name('article')
        info_ele = article_ele.find_element_by_class_name('info')
        time_ele = info_ele.find_element_by_class_name('time')
        content_ele = self.driver.find_element_by_class_name('news-content')
        p_ele = content_ele.find_elements_by_xpath('p')
        if len(p_ele) == 0:
            div_ele = content_ele.find_elements_by_xpath('div')
            for x in div_ele:
                p_ele.extend(x.find_elements_by_xpath('p'))
        content = ''
        for x in p_ele:
            if not x.text: continue
            content += x.text.strip()
            if len(content) >= 64:
                break
        return time_ele.text, content

if __name__ == '__main__':
    Spider('baijia', 'https://baijia.baidu.com/channel?cat=1').start()
