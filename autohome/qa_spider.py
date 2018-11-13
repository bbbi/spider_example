# -*- coding: utf-8 -*-
import hashlib
import re
import time
from copy import deepcopy
from queue import Queue
from threading import Thread
from urllib.parse import urljoin

import requests
from fake_useragent import UserAgent
from lxml import etree
from pymongo import MongoClient
from redis.client import StrictRedis


def __get_hash(url, method, *args):
    hash = hashlib.sha1()
    if url and method:
        hash.update(url.encode('utf-8'))
        hash.update(method.encode('utf-8'))
        if args:
            for a in args:
                hash.update(a.encode('utf-8'))

    hash_str = hash.hexdigest()
    return hash_str


def test_url_by_redis(redis_db, key, url, method, *args):
    if isinstance(redis_db, StrictRedis):
        value = __get_hash(url, method, *args)
        # print(value)
        return redis_db.sadd(key, value)


class QaBaseSpider:
    def __init__(self, start_url=None):
        self.start_url = start_url
        self.base_request = Queue()

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
        content = response.text
        return content

    def xpath_html(self, content):
        html = etree.HTML(content)
        return html

    def get_one_level(self):
        content = self.parse_url(self.start_url)  # 获取起始页
        html = self.xpath_html(content)
        a_list = html.xpath("//div[@class='classify'][1]//a")
        __temp_list = []
        for a in a_list:
            item = dict()
            item['one_level_url'] = a.xpath("./@href")[0]
            item['one_level_url'] = urljoin(self.start_url, item['one_level_url'])
            item['one_level_name'] = a.xpath(".//em/text()")[0]
            __temp_list.append(item)
        return __temp_list

    def get_two_level(self, item):
        content = self.parse_url(item['one_level_url'])
        html = self.xpath_html(content)
        a_list = html.xpath("//div[@class='classify'][2]//a")
        if len(a_list) == 0:
            item['menu_url'] = item['one_level_url']
            self.base_request.put(deepcopy(item))
            return []
        __temp_list = []
        print('len', len(a_list))
        for a in a_list:
            item['two_level_url'] = a.xpath("./@href")[0]
            item['two_level_url'] = urljoin(self.start_url, item['two_level_url'])
            item['two_level_name'] = a.xpath(".//em/text()")[0]
            __temp_list.append(deepcopy(item))
        return __temp_list

    def get_sec_level(self, item):
        content = self.parse_url(item['two_level_url'])
        html = self.xpath_html(content)
        a_list = html.xpath("//div[@class='classify'][3]//a")
        if len(a_list) == 0:
            item['menu_url'] = item['two_level_url']
            self.base_request.put(deepcopy(item))
            return []
        for a in a_list:
            item['sec_level_url'] = a.xpath("./@href")[0]
            item['sec_level_url'] = urljoin(self.start_url, item['sec_level_url'])
            item['sec_level_name'] = a.xpath(".//em/text()")[0]
            item['menu_url'] = item['sec_level_url']
            self.base_request.put(deepcopy(item))

    def build_base_url(self):
        for one in self.get_one_level():
            for two in self.get_two_level(one):
                self.get_sec_level(two)

    def test(self):
        """
        测试函数
        :return: None
        """
        self.start_url = "https://wenda.autohome.com.cn/topic/list-0-0-0-0-0-1"
        self.build_base_url()
        while not self.base_request.empty():
            print(self.base_request.get())

    def run(self):
        pass


class QaDetailSpider(QaBaseSpider):
    def __init__(self, start_url=None):
        super().__init__(start_url)
        # 初始化redis数据库
        self.redis_key = 'CarQaFilter'
        self.redis_db = StrictRedis(host='127.0.0.1', port=6379, db=1)

        # 初始化mongodb数据库
        self.mongo_client = MongoClient()
        self.collection = self.mongo_client['autocar']['qa']

        # 详情页队列
        self.detail = Queue()

        # re预编译
        self.clean_detail = re.compile(r'\s|\n')

    def build_detail_url(self, item):
        list_url = item['menu_url']
        content = self.parse_url(list_url)
        html = self.xpath_html(content)
        li_list = html.xpath("//ul[@class='question-list']/li")  # 分组
        for li in li_list:
            item['q_title'] = li.xpath("./h4/a/text()")[0]
            item['q_url'] = li.xpath("./h4/a/@href")[0]
            item['q_url'] = urljoin(self.start_url, item['q_url'])  # url 拼接
            item['q_time'] = li.xpath("./span[@class='date']/@date-time")[0]
            item['a_count'] = li.xpath("./span[@class='count']/text()")[0]
            item['a_count'] = re.findall(r'(\d+)', item['a_count'])[0]
            # 将解析结果放入队列中
            self.detail.put(deepcopy(item))
        # 翻页
        next_url = html.xpath("//a[@class='athm-page__next']/@href")[0] if len(
            html.xpath("//a[@class='athm-page__next']/@href")) > 0 else None
        if next_url:
            next_url = urljoin(self.start_url, next_url)
            item['menu_url'] = next_url
            self.build_detail_url(item)

    def get_detail_url(self):
        while not self.base_request.empty():
            item = self.base_request.get()  # 取基础页url
            self.build_detail_url(item)  # 解析目录页，获取详情页数据
            self.base_request.task_done()  # 解析完成后，调用队列回调函数

    def get_detail(self):
        while not self.detail.empty():
            print("—" * 10, '目前详情页队列剩余：', self.detail.qsize(), "—" * 10)
            item = self.detail.get()
            detail_url = item['q_url']
            a_count = item['a_count']
            # 去重
            redis_status = test_url_by_redis(self.redis_db, self.redis_key, detail_url, "GET", a_count)
            if redis_status:
                content = self.parse_url(detail_url)
                html = self.xpath_html(content)
                # 解析详情页
                item['q_user'] = html.xpath("//div[@class='card-wrap']/p/span/a/text()")[0]
                item['q_user_url'] = "https:" + html.xpath("//div[@class='card-wrap']/p/span/a/@href")[0]
                item['q_info'] = html.xpath("//div[@class='card-wrap']/div[@class='card-content ']//p/text()")
                # 解析回答详情页
                div_list = html.xpath("//div[@id='replyContent']/div")
                __temp_list = []
                for div in div_list:
                    temp = {}
                    temp['a_user'] = div.xpath("./div[1]/div[1]/a[2]/text()")[0]
                    temp['a_user_url'] = "https:" + div.xpath("./div[1]/div[1]/a[2]/@href")[0]
                    temp['a_user_level'] = "https:" + div.xpath("./div[1]/div[1]/img/@src")[0] if len(
                        div.xpath("./div[1]/div[1]/img/@src")) > 0 else '无等级'
                    temp['a_detail'] = div.xpath("./div[2]/div/a/text()")[0]
                    temp['a_detail'] = self.clean_detail.sub('', temp['a_detail'])
                    temp['a_detail_url'] = div.xpath("./div[2]/div/a/@href")[0]
                    temp['a_detail_url'] = urljoin(self.start_url, temp['a_detail_url'])
                    temp['a_up'] = div.xpath("./div[3]/a[1]/span[1]/text()")[0]
                    temp['a_down'] = div.xpath("./div[3]/a[2]/span[1]/text()")[0]
                    __temp_list.append(temp)

                # 回答放入字典
                item['a_info'] = __temp_list
                self.save_item(item)
                # 队列回调函数
                self.detail.task_done()
            else:
                print("去重", '-' * 100)
                # 队列回调函数
                self.detail.task_done()

    def save_item(self, item):
        self.collection.insert(item)
        print("插入成功", item['q_info'])

    def run(self):
        self.build_base_url()  # 构建基础url
        t_list = []
        # 目录线程
        for i in range(2):
            t1 = Thread(target=self.get_detail_url, daemon=True)
            t_list.append(t1)
        # 详情线程
        for i in range(8):
            t2 = Thread(target=self.get_detail, daemon=True)
            t_list.append(t2)

        # 启动线程
        for s in t_list:
            s.start()
            time.sleep(2)
        # 队列等待
        self.base_request.join()
        self.detail.join()


if __name__ == '__main__':
    qa = QaDetailSpider(start_url="https://wenda.autohome.com.cn/topic/list-0-0-0-0-0-1")
    qa.run()
