from browser import PhantomJS
from lxml import etree
import requests
import re

class Spider(PhantomJS):
    """docstring for Spider"""
    def __init__(self, name, home_page):
        super(Spider, self).__init__(name, home_page)
          
    def parse_page(self):
        news_ele = self.driver.find_element_by_class_name('newsdata_item')
        news_ele = news_ele.find_elements_by_css_selector('.data_row.news_article.clearfix')
        for x in news_ele:
            title_ele = x.find_element_by_xpath('.//div[@class="news_title"]/h3/a')
            title = title_ele.text
            if not title or title in self.items_dict: continue
            self.logger.info(title)
            url = title_ele.get_attribute("href")
            try:
                source, dt, content = self.get_detail_page(url)
            except Exception as e:
                print(e)
                continue

            keywords = []
            keywords_ele = x.find_elements_by_xpath('.//div[@class="keywords"]/a')
            for y in keywords_ele:
                keywords.append(y.text.strip())
            item_data = self.item.copy()
            item_data['source'] = source
            item_data['title'] = title
            item_data['url'] = url
            item_data['keywords'] = ','.join(keywords)
            item_data['content'] = content
            item_data['datetime'] = dt
            self.save_item(item_data)

    def get_detail_page(self, page):
        """ 获取详情页信息 """
        r = requests.get(page)
        tree = etree.HTML(r.text)
        infolist = tree.xpath('//div[@class="post_content_main"]')[0]
        dt_ele = infolist.xpath('div[@class="post_time_source"]')[0]
        source_ele = dt_ele.xpath('a[@id="ne_article_source"]')[0]
        contet_ele = infolist.xpath('div[@class="post_body"]')[0]
        contet_ele = contet_ele.xpath('div[@class="post_text"]')[0]
        p = contet_ele.xpath('p')
        pattern = re.compile(r'\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}')
        dt = re.findall(pattern, dt_ele.text)[0]
        content = ''
        for x in p:
            if not x.text: continue
            content += x.text.strip()
            if len(content) >= 64:
                break
        return source_ele.text, dt, content

Spider('163', 'http://tech.163.com/smart/').start()