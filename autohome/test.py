# -*- coding: utf-8 -*-
from urllib.parse import urljoin

import requests
from lxml import etree
import re

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
}

#
# response = requests.get("https://wenda.autohome.com.cn/topic/detail/143516",headers=headers)
#
# html = etree.HTML(response.text)
#
# div_list = html.xpath("//div[@id='replyContent']/div")
#
# print(len(div_list))

print(re.findall(r'(\d+)','3回答')[0])

print(urljoin("http://maoyan.com/films","?sortId=1&offset=30"))
print(urljoin("http://maoyan.com/films","/static/?sortId=1&offset=30"))