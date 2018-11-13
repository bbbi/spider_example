# -*- coding: utf-8 -*-
import time

from pymongo import MongoClient
from selenium import webdriver


# 实例化一个数据库集合
client = MongoClient(host="127.0.0.1", port=27017)
collection = client['panzhi']['info_2018_10_26']

# 实例化一个选项对象
options = webdriver.FirefoxOptions()
# 添加无头参数
options.add_argument("--headless")
# 实例化一个浏览器对象
# driver = webdriver.Firefox(options=options)
driver = webdriver.Firefox()

# 发送请求获取相应
driver.get("http://panzhids.com/show.aspx?ys=0")
count = 1
while True:
    # 解析数据
    context_list = driver.find_elements_by_xpath("//div[@class='list ']/div")  # 数据div
    page = driver.find_elements_by_xpath(
        "//div[@id='ctl00_ctl00_ContentPlaceHolder1_ContentPlaceHolder2_AspNetPager2']/a")
    next = None
    for i in page:
        if i.text == '下一页':
            next = i
            break

    for i in context_list:
        item = {}
        item["url_info"] = i.find_element_by_xpath("./a").get_attribute("href")
        item["info"] = i.find_element_by_xpath("./a/div[@class='wz_wd1']").text
        item["price"] = i.find_element_by_xpath("./a/div[@class='wz_wd2']/span[@class='w1']/span").text
        item["region"] = i.find_element_by_xpath("./a/div[@class='wz_wd2']/span[@class='w2']").text[3:]
        item["serve"] = i.find_element_by_xpath("./a/div[@class='wz_wd2']/span[@class='w3']").text[4:]
        item["personage"] = i.find_element_by_xpath("./a/div[@class='wz_wd2']/span[@class='w4']").text[3:]
        item["time"] = i.find_element_by_xpath("./a/div[@class='wz_wd2']/span[@class='w5']").text[5:]
        collection.insert(item)

    print('-' * 10)
    if next.get_attribute('href') == None:
        print("完成")
        driver.quit()
        break

    next.click()
    print(count)
    count += 1
    time.sleep(4)
