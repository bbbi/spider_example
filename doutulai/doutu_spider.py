# -*- coding: utf-8 -*-
import os
import re
import threading
import time
from queue import Queue
from threading import Thread
from urllib.parse import urljoin
import requests
from fake_useragent import UserAgent
from lxml import etree


class DoutuSpider:
    def __init__(self, start_url):
        self.start_url = start_url
        self.detail = Queue()
        self.headers = {
            "User-Agent": UserAgent().random
        }

    def parse_url(self, url):
        response = requests.get(url, headers=self.headers)
        content = response.content
        return content

    def parse_content(self):
        content = self.parse_url(self.start_url)
        html = etree.HTML(content)  # 格式化网页
        a_list = html.xpath("//div[@class='col-sm-9']/a")  # 分组
        for a in a_list:
            detail_url = a.xpath("./@href")[0] if len(a.xpath("./@href")) > 0 else None  # 获取详情页url
            self.detail.put(detail_url)  # 将详情页队列
        # 提取下一页的URL 如果没有则为None
        next_url = html.xpath("//a[@rel='next']/@href")[0] if len(html.xpath("//a[@rel='next']/@href")) > 0 else None

        while next_url:
            next_url = urljoin(self.start_url, next_url)
            self.start_url = next_url
            self.parse_content()

    def save_img(self):
        while True:
            detail_url = self.detail.get()
            content = self.parse_url(detail_url)
            html = etree.HTML(content)
            title = html.xpath("//h1/a/text()")[0]
            try:
                os.mkdir(os.path.join(os.getcwd(), 'images', title))
            except Exception as e:
                print(e)
                continue
            img_list = html.xpath("//div[@class='artile_des']")
            for i in img_list:
                img_url = i.xpath(".//img/@src")[0]
                if i.xpath(".//img/@src")[0] == '':
                    __temp = i.xpath(".//img/@onerror")[0]
                    img_url = re.search(r"this.src='(.*)'", __temp).group(1)
                img_title = i.xpath(".//img/@alt")[0]
                img_title = re.sub(r'[?？。."]', '', img_title)
                try:
                    img = self.parse_url(img_url)
                except:
                    img = ''
                    print(img_url, img_title)
                img_name = os.path.join(os.getcwd(), 'images', title, img_title, ) + os.path.splitext(img_url)[1]
                try:
                    with open(img_name, 'wb') as f:
                        f.write(img)
                except:
                    print(img_name, "未写入完成")
            print(title, "下载完成")
            self.detail.task_done()
            time.sleep(1)

    def run(self):
        t1 = Thread(target=self.parse_content)
        t1.start()
        time.sleep(5)
        t_list = []

        for i in range(5):
            t2 = Thread(target=self.save_img)
            t_list.append(t2)

        for t in t_list:
            t.setDaemon(True)
            t.start()

        self.detail.join()

    def run1(self):
        t1 = Thread(target=self.parse_content)
        t1.start()
        time.sleep(10)
        t_list = []

        while True:
            if len(threading.enumerate()) < 10:
                t2 = Thread(target=self.save_img)
                t_list.append(t2)
                t2.setDaemon(True)
                t2.start()
            print("当前线程数", len(threading.enumerate()), "---------------")
            time.sleep(2)
            if self.detail.empty():
                break


if __name__ == '__main__':
    tu = DoutuSpider("http://www.doutula.com/article/list/?page=20")
    tu.run1()
