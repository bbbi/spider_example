# -*- coding: utf-8 -*-
from selenium import webdriver

class PanzhiSpider:
    """天刀盼之的爬虫"""
    def __init__(self):
        self.start_url = "http://panzhids.com/show.aspx?ys=0"
        self.driver = webdriver.Chrome()



    def get_context_list(self, driver):
        pass

    def run(self):
        # 发送请求，利用selenium，得到网页的源码
        # 解析数据
        # 保存数据到mongodb，panzhi,info中
        # 判断是否有下一页并保存

        pass
