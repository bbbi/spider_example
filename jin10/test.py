#-*- coding: utf-8 -*-
import re

import requests
from lxml import etree

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
}

response = requests.get(url="https://www.jin10.com/", headers=headers)

# html = etree.HTML(response.content)

data = re.findall(r'var flashData = \[""', response.content.decode('utf-8'))
print(data)
# print(data)
# div_list = html.xpath("//div[@id='J_flashList']/div")
#
# for div in div_list:
#     time = div.xpath("./div[1]//text()")[0]
#     title = div.xpath("./div[2]//text()")[0] if len(div.xpath("./div[2]//text()")) > 0 else None
#     print(time)
#     print(title)




# import hashlib
#
# from redis import StrictRedis


# def __get_hash(data):
#     hash = hashlib.sha1()
#     if data:
#         hash.update(data.encode('utf-8'))
#     hash_str = hash.hexdigest()
#     return hash_str
#
#
# def test_url_by_redis(redis_db, data):
#     key = "jin10"
#     if isinstance(redis_db, StrictRedis):
#         value = __get_hash(data)
#         # print(value)
#         return redis_db.sadd(key, value)
#
#
# if __name__ == '__main__':
#     redis_db = StrictRedis()
#     print(test_url_by_redis(redis_db, "2"))
