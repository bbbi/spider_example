# -*- coding: utf-8 -*-
from queue import Queue
from urllib.parse import urljoin

import requests
from fake_useragent import UserAgent
from lxml import etree
from selenium import webdriver


class BaseSpider:
    """
    爬虫基础请求及解析类
    """

    def parse_url(self, url):
        """
        发送请求并返回响应
        :param url: 完整的url
        :return: 返回str类型文本
        """
        headers = {
            'User-Agent': UserAgent().random
        }
        response = requests.get(url, headers=headers)
        content = response.content
        return content

    def xpath_html(self, content):
        html = etree.HTML(content)
        return html


class HotMoviesSpider(BaseSpider):
    def __init__(self, start_url):
        # 加载父类___init__方法
        super(HotMoviesSpider, self).__init__()
        # 起始url
        self.start_url = start_url
        # 详情页队列
        self.detail = Queue()

    def get_detail_url(self, url):
        content = self.parse_url(url).decode('utf-8')  # 解析url
        html = self.xpath_html(content)  # 格式化文本对象
        # 分组
        dd_list = html.xpath("//dl[@class='movie-list']/dd")
        # 遍历分组取得详情页url
        for dd in dd_list:
            item = dict()
            item['movie_name'] = dd.xpath("./div[2]/a/text()")[0]
            item['movie_detail_url'] = dd.xpath("./div[2]/a/@href")[0]
            item['movie_detail_url'] = urljoin(self.start_url, item['movie_detail_url'])  # 拼接url
            item['movie_score'] = dd.xpath("./div[3]/text()")
            item['movie_cover'] = dd.xpath("./div[1]/a/div/img[last()]/@src")
            # 放入详情页队列
            self.detail.put(item)

        # 处理翻页问题
        next_url = html.xpath("//a[text()='下一页']/@href") if len(html.xpath("//a[text()='下一页']/@href")) > 0 else None

        if next_url:
            next_url = urljoin(self.start_url, next_url)
            self.get_detail_url(next_url)

    def get_detail(self):
        while not self.detail.empty():
            print('-' * 20, '目前详情队列数量：', self.detail.qsize(), '-' * 20)
            item = self.detail.get()
            detail_url = item['movie_detail_url']  # 获取详情页url
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome()
            driver.get(detail_url)
            item['movie_english_name'] = driver.find_element_by_xpath(
                "//div[@class='wrapper clearfix']/div[2]/div[1]/div").text

    def test(self):
        self.start_url = "http://maoyan.com/films/246596"

    def run(self):
        "破产"
        pass
