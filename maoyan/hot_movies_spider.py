# -*- coding: utf-8 -*-
import os
from queue import Queue
from urllib.parse import urljoin
from A.maoyan.discern_font import get_num_mapping
import requests
from fake_useragent import UserAgent
from lxml import etree



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

    def create_font(self, font_file):
        # 列出已下载文件
        file_list = os.listdir(os.path.join(os.getcwd(), "fonts"))
        new_path = os.path.join(os.getcwd(), 'fonts', font_file)
        # 判断是否已下载
        if font_file not in file_list:
            # 未下载则下载新库
            print('不在字体库中, 下载:', font_file)
            url = 'http://vfile.meituan.net/colorstone/' + font_file
            new_file = self.parse_url(url)
            with open(new_path, 'wb') as f:
                f.write(new_file)
        return new_path

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
            content = self.parse_url(detail_url)
            html = self.xpath_html(content)
            # 处理电影简介信息
            item['movie_english_name'] = html.xpath("//div[@class='wrapper clearfix']/div[2]/div[1]/div/text()")[0]
            item['movie_category'] = html.xpath("//div[@class='wrapper clearfix']/div[2]/div[1]/ul/li[1]/text()")[0]
            item['movie_time'] = html.xpath("//div[@class='wrapper clearfix']/div[2]/div[1]/ul/li[2]/text()")[0]
            item['movie_show_date'] = html.xpath("//div[@class='wrapper clearfix']/div[2]/div[1]/ul/li[3]/text()")[0]
            # 处理电影内容信息

    def run(self):
        pass

    def test(self):
        path = self.create_font("47b01555f36a1243ea7aecbbb28dd81e2076.woff")
        print(path)
        mapping = get_num_mapping(path)
        print(mapping)


if __name__ == '__main__':
    m = HotMoviesSpider(None)
    m.test()
