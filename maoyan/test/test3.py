# -*- coding: utf-8 -*-
from selenium import webdriver

driver = webdriver.Chrome()
driver.set_window_size(900,600)

driver.get("http://maoyan.com/films/1203437")

a = driver.find_element_by_xpath("//div[@class='wrapper clearfix']/div[2]/div[1]/div").text
driver.save_screenshot('./3.png')

print(a)
# driver.close()
