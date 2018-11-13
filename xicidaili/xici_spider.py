# -*- coding: utf-8 -*-
from queue import Queue
from threading import Thread

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from redis.client import StrictRedis


class XiciSpider:
    def __init__(self, size=5, test_url="http://www.baidu.com"):
        self.test_url = test_url
        self.size = size
        self.redis_db = StrictRedis()
        # 队列
        self.proxy = Queue()
        self.headers = {
            "User-Agent": UserAgent().chrome
        }

    def build_url(self):
        url_list = []  # 创建一个保存URL的列表
        base_url = "http://www.xicidaili.com/nn/{}"  # 基础url
        # 构建新的URL
        for page in range(1, int(self.size) + 1):
            new_url = base_url.format(page)
            url_list.append(new_url)
        print(url_list)
        return url_list

    def parse(self, url_list):
        # 发送请求获取响应
        for url in url_list:
            response = requests.get(url, headers=self.headers)
            content = response.content.decode()
            self.parse_content(content)

    def parse_content(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        tr_list = soup.select("table#ip_list tr")[1:]  # 分组
        for tr in tr_list:
            item = {}
            item['ip'] = tr.select("td")[1].get_text()
            item['port'] = tr.select("td")[2].get_text()
            item['scheme'] = tr.select("td")[5].get_text()
            # print(item)
            self.proxy.put(item)

    def test_ip(self):
        while True:
            item = self.proxy.get()  # 获取一个待检测ip对象
            if item['scheme'] == 'HTTPS':
                test_ip = "https://" + item['ip'] + ":" + item['port']
            else:
                test_ip = "http://" + item['ip'] + ":" + item['port']
            try:
                if item['scheme'] == 'HTTPS':
                    # 检测
                    proxies = {
                        "https": test_ip
                    }
                else:
                    proxies = {
                        "http": test_ip
                    }
                response = requests.get(self.test_url, headers=self.headers, proxies=proxies, timeout=5)
                if response.status_code == 200:
                    # print(test_ip, "代理可用")
                    self.save_ip(test_ip, item['scheme'])
                self.proxy.task_done()
            except Exception as e:
                # print(e)
                print(test_ip, "不可用")
                self.proxy.task_done()

    def save_ip(self, test_ip, scheme):
        if scheme == 'HTTPS':
            key = "https"
        else:
            key = "http"

        try:
            self.redis_db.sadd(key, test_ip)
            print("添加成功", test_ip)
        except Exception as e:
            print(e)

    def run(self):
        url_list = self.build_url()
        self.parse(url_list)
        # 启动批量检测线程，提取可用ip 并保存
        t_list = []
        for i in range(10):
            print("启动检测线程", i)
            t = Thread(target=self.test_ip)
            t_list.append(t)

        for i in t_list:
            i.setDaemon(True)
            i.start()

        self.proxy.join()


if __name__ == '__main__':
    t = XiciSpider(size=5)
    t.run()
