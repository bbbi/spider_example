# -*- coding: utf-8 -*-
import hashlib
import re
import time
import requests
from lxml import etree
from pymongo import MongoClient
from redis import StrictRedis


def __get_hash(data):
    hash = hashlib.sha1()
    if data:
        hash.update(data.encode('utf-8'))
    hash_str = hash.hexdigest()
    return hash_str


def test_url_by_redis(redis_db, data):
    key = "jin10"
    if isinstance(redis_db, StrictRedis):
        value = __get_hash(data)
        # print(value)
        return redis_db.sadd(key, value)

class Jin10Spider:

    def __init__(self):
        self.url = "https://www.jin10.com/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        }
        self.s = requests.session()

        self.client = MongoClient()
        self.coll = self.client['jin10']['data']
        self.redis_db = StrictRedis()

    def parse(self):
        response = self.s.get(self.url, headers=self.headers)

        return response.content

    def xpath_content(self, content):
        html = etree.HTML(content)
        return html

    def parse_content(self, html, temp):
        div_list = html.xpath("//div[@id='J_flashList']/div")
        data = re.search(r'var flashData = \[".*?(\w+-\w+-\w+)', temp).group(1)
        __temp = []
        for div in div_list:
            item = {}
            item['datetime'] = str(data) + ' ' + div.xpath("./div[1]//text()")[0] if len(
                div.xpath("./div[1]//text()")) > 0 else None
            item['title'] = div.xpath("./div[2]//text()")[0] if len(div.xpath("./div[2]//text()")) > 0 else None
            # print(item)
            __temp.append(item)
        return __temp

    def save(self, data_list):
        # sat = set()
        for item in data_list:
            # if not sat.add(str(item)):
            #     print(item)
            #     self.coll.insert(item)
            if test_url_by_redis(self.redis_db,str(item)):
                self.coll.insert(item)
                print('--------------------')
                print(item)

    def run(self):
        content = self.parse()
        html = self.xpath_content(content)
        data_list = self.parse_content(html, content.decode('utf-8'))
        self.save(data_list)


if __name__ == '__main__':
    while True:
        jin = Jin10Spider()
        jin.run()
        time.sleep(10)
