from browser import Firefox
import re

class Spider(Firefox):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('newsdata_item')
        news_ele = news_ele.find_elements_by_css_selector('.data_row.news_article.clearfix')
        item_list = []
        for x in news_ele:
            title_ele = x.find_element_by_xpath('.//div[@class="news_title"]/h3/a')
            title = title_ele.text
            if not title or title in self.items_dict: continue
            self.logger.info(title)
            url = title_ele.get_attribute("href")
            keywords = []
            keywords_ele = x.find_elements_by_xpath('.//div[@class="keywords"]/a')
            for y in keywords_ele:
                keywords.append(y.text.strip())

            item_data = self.item.copy()
            item_data['title'] = title
            item_data['url'] = url
            item_data['keywords'] = ','.join(keywords)
            item_list.append(item_data)

        for x in item_list:
            self.get_page(x['url'])
            try:
                x['source'], x['datetime'], x['content'] = self.parse_detail_page()
                self.save_item(x)
            except Exception as e:
                print(e)

    def parse_detail_page(self):
        """ 获取详情页信息 """
        info_ele = self.driver.find_element_by_class_name('post_content_main')
        time_ele = info_ele.find_element_by_class_name('post_time_source')
        source_ele = time_ele.find_element_by_id('ne_article_source')
        contet_ele = info_ele.find_element_by_class_name('post_body')
        contet_ele = contet_ele.find_element_by_class_name('post_text')
        p = contet_ele.find_elements_by_tag_name('p')
        pattern = re.compile(r'\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}')
        dt = re.findall(pattern, time_ele.text)[0]
        content = ''
        for x in p:
            if not x.text: continue
            content += x.text.strip()
            if len(content) >= 64:
                break
        return source_ele.text, dt, content

## Spider('163', 'http://tech.163.com/smart/').start()