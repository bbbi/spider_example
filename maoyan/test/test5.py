# -*- coding: utf-8 -*-
import requests
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Nexus 6P Build/OPP3.170518.006) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.92 Mobile Safari/537.36',
}

response = requests.get("http://m.maoyan.com/movie/1203437?_v_=yes", headers=headers)

html = etree.HTML(response.content)

print('票房为(万)：', html.xpath("//p[@class='num']/text()")[2])
