# -*- coding: utf-8 -*-
import re
from queue import Queue
from threading import Thread
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pymysql.connections import Connection


class Ip89Spider:
    def __init__(self, size=5, test_url="http://www.baidu.com"):
        self.test_url = test_url
        self.size = size
        # 数据库相关
        self.db = Connection(host='127.0.0.1', port=3306, user='root', password='123456', database='proxy_ip')
        self.cour = self.db.cursor()
        # 正则预编译
        self.rer = re.compile(r"\n|\t")
        # 队列对象
        self.proxy = Queue()
        self.ip = Queue()
        # 请求头
        self.headers = {
            "User-Agent": UserAgent().chrome
        }

    def build_url(self):
        url_list = list()  # 创建一个保存URL的列表
        base_url = "http://www.89ip.cn/index_{}.html"  # 基础url
        # 构建新的URL
        for page in (1, int(self.size) + 1):
            new_url = base_url.format(page)
            url_list.append(new_url)
        return url_list

    def parse(self, url_list):
        # 发送请求获取响应
        for url in url_list:
            response = requests.get(url, headers=self.headers)
            content = response.content.decode()
            self.parse_content(content)

    def parse_content(self, content):
        soup = BeautifulSoup(content, 'lxml')
        tr_list = soup.select("div[class='layui-form'] tbody tr")  # 分组
        for tr in tr_list:
            item = {}
            item['ip'] = tr.select("td")[0].get_text()
            item['ip'] = self.rer.sub('', item['ip'])
            item['port'] = tr.select("td")[1].get_text()
            item['port'] = self.rer.sub('', item['port'])
            print(item)
            self.proxy.put(item)

    def test_ip(self):
        while True:
            item = self.proxy.get()  # 获取一个待检测ip对象
            test_ip = "http://" + item['ip'] + ":" + item['port']
            try:
                # 检测
                proxies = {
                    "http": test_ip
                }
                response = requests.get(self.test_url, headers=self.headers, proxies=proxies, timeout=5)
                if response.status_code == 200:
                    print(test_ip, "代理可用")
                    self.save_ip(test_ip)
                self.proxy.task_done()
            except Exception as e:
                print(e)
                print(test_ip, "不可用")
                self.proxy.task_done()

    def save_ip(self, test_ip):
        SQL = "INSERT INTO t_ip (ip) VALUES (%s)"
        print(SQL)
        self.cour.execute(SQL, args=(test_ip,))
        self.db.commit()
        print("保存成功")

    def run(self):
        url_list = self.build_url()  # 构建url
        self.parse(url_list)  # 解析url
        # 启动批量检测线程，提取可用ip 并保存
        t_list = []
        for i in range(5):
            print("启动检测线程", i)
            t = Thread(target=self.test_ip)
            t_list.append(t)

        for i in t_list:
            i.setDaemon(True)
            i.start()
        self.proxy.join()


if __name__ == '__main__':
    t = Ip89Spider()
    t.run()
    # t.test()
