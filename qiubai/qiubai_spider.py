# -*- coding: utf-8 -*-
import json
import re
from urllib import request, parse
from fake_useragent import UserAgent
from lxml import etree


class QiubaiSpider:
    def __init__(self, start_url):
        self.ua = UserAgent()
        self.start_url = start_url
        self.headers = {
            "User-Agent": self.ua.chrome
        }

    def parse_url(self, url):
        _request = request.Request(url, headers=self.headers)  # 构建请求对象
        print(_request.headers)
        response = request.urlopen(_request)  # 发送请求获取相应
        return response

    def parse_response(self, response):
        print(response.info())
        content_lxml = etree.HTML(response.read())  # LXML化相应
        div_list = content_lxml.xpath("//div[@id='content-left']/div")  # 获取div快列表
        # 解析数据并保存到列表中
        content = []
        for div in div_list:
            item = {}
            item['author'] = div.xpath(".//h2/text()")[0]
            item['author'] = re.sub(r'\n', '', item['author'])
            item['content'] = div.xpath(".//div[@class='content']//text()")
            item['content'] = ''.join(item['content'])
            item['content'] = re.sub(r'\n', '', item['content'])
            content.append(item)

        # 解析下一页的url
        next_text = content_lxml.xpath("//span[@class='next']/text()")[0]
        next_text = re.sub(r'\n', '', next_text)
        print(next_text)
        if next_text == "下一页":
            next_url = content_lxml.xpath("//span[@class='next']/../@href")[0]
            print(next_url)
            next_url = parse.urljoin(self.start_url, next_url)
        else:
            next_url = None

        return content, next_url

    def save_content(self, content):
        for con in content:
            with open('./qiubai.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(con,ensure_ascii=False))
                f.write(','+'\n')

    def run(self):
        while True:
            print(self.start_url)
            response = self.parse_url(self.start_url)  # 解析url
            content, next_url = self.parse_response(response)
            self.save_content(content)
            if next_url:
                self.start_url = next_url
            else:
                break


if __name__ == '__main__':
    hot = QiubaiSpider("https://www.qiushibaike.com/hot/page/1/")
    hot.run()
