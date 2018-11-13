# -*- coding: utf-8 -*-
import json
import time
from queue import Queue
from threading import Thread
from urllib.parse import urljoin

import requests
from fake_useragent import UserAgent
from lxml import etree


class CarInfoSpider:
    def __init__(self, start_url):
        self.start_url = start_url  # 爬虫入口
        self.detail = Queue()  # 详情页队列
        # 请求头
        self.headers = {
            "User-Agent": UserAgent().random,
            "Host": "car.autohome.com.cn"
        }

    def parse_url(self, url):
        """
        发送请求并返回响应
        :param url: 完整的url
        :return: 返回str类型文本
        """
        response = requests.get(url, headers=self.headers)
        content = response.text
        return content

    def xpath_content(self):
        """
        解析目录页获取一级标题及url
        :return: 将item对象放入队列
        """
        content = self.parse_url(self.start_url)  # 解析url
        html = etree.HTML(content)  # 格式化
        li_list = html.xpath("/html/body/ul/li")  # 分组
        # 提取标题及url并放入到队列中
        for li in li_list:
            item = dict()
            item['first_name'] = li.xpath("./h3/a/text()")[0]
            item['first_url'] = li.xpath("./h3/a/@href")[0]
            item['first_url'] = urljoin(self.start_url, item['first_url'])
            self.detail.put(item)

    def xpath_detail(self):
        """
        继续解析并保存
        :return: None
        """
        while True:
            item = self.detail.get()
            first_url = item['first_url']
            content = self.parse_url(first_url)
            html = etree.HTML(content)
            div_list = html.xpath("//div[@class='list-cont']")
            for div in div_list:
                item['car_name'] = div.xpath(".//div[@class='list-cont-main']/div/a/text()")[0]
                item['level'] = div.xpath(
                    ".//div[@class='main-lever-left']/ul[@class='lever-ul']/li[1]/span[@class='info-gray']/text()")[0]
                item['engine'] = div.xpath(
                    ".//div[@class='main-lever']/div[@class='main-lever-left']/ul[@class='lever-ul']/li[3]/span/a/text()")

                item['price'] = div.xpath(
                    ".//div[@class='list-cont-main']/div[@class='main-lever']/div[@class='main-lever-right']/div[1]/span[@class='lever-price red']/span/text()")[
                    0]
                print(item)
                self.save_info(item)
            self.detail.task_done()

    def save_info(self, item):
        """
        格式化并保存数据
        :param item: 字典对象
        :return: None
        """
        with open('carInfo_test.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(item, ensure_ascii=False))
            f.write(',')
            f.write('\n')

    def run(self):
        self.xpath_content()
        print(self.detail.qsize())
        for i in range(4):
            print(i)
            t = Thread(target=self.xpath_detail, daemon=True)
            t.start()

        self.detail.join()


if __name__ == '__main__':
    start_time = time.time()
    car = CarInfoSpider(
        "https://car.autohome.com.cn/AsLeftMenu/As_LeftListNew.ashx?typeId=1%20&brandId=0%20&fctId=0%20&seriesId=0")
    car.run()
    end_time = time.time()
    print(start_time - end_time)
