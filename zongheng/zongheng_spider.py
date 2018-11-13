# -*- coding: utf-8 -*-
from fake_useragent import UserAgent
from lxml import etree
from pymysql.connections import Connection
from requests import Request, Session


class ZonghengSpider:
    def __init__(self, start_url):
        self.start_url = start_url
        self.db = Connection(host='127.0.0.1', port=3306, user='root', password='123456', db='books')
        self.cur = self.db.cursor()
        self.s = Session()
        self.headers = {
            "User-Agent": UserAgent().chrome
        }

    def build_request(self, start_url):
        _temp = Request(method='GET', url=start_url, headers=self.headers)  # 构建请求对象
        _request = _temp.prepare()  # 准备请求对象
        return _request

    def parse_request(self, request):
        response = self.s.send(request)  # 发送请求获取响应
        content = response.content  # 获取bytes文本对象
        return content

    def parse_content(self, content):
        content_lxml = etree.HTML(content)  # 格式化页面
        div_list = content_lxml.xpath("//div[@class='rankpage_box']/div[@class='rank_d_list borderB_c_dsh clearfix']")
        # 提取数据
        content_list = []
        for div in div_list:
            item = {}
            item['title'] = div.xpath("./@bookname")[0]
            item['author'] = div.xpath(".//div[@class='rank_d_b_cate']/@title")[0]
            item['img'] = div.xpath(".//img/@src")[0]
            item['intro'] = div.xpath(".//div[@class='rank_d_b_info']/text()")[0]
            content_list.append(item)
        # # 提取下一页url
        # total_page = content_lxml.xpath("//div[@class='rank_d_pagesize pagebar']/@count")[0]
        # print(total_page)
        return content_list

    def save_content(self, content_list):
        for item in content_list:
            title = item.get("title", '')
            author = item.get("author", '')
            img = item.get("img", '')
            intro = item.get("intro", '')
            SQL = "INSERT INTO t_zongheng (title, author, img, intro) VALUES ('%s','%s','%s','%s')" % (
            title, author, img, intro)
            # SQL = "INSERT INTO t_zongheng (title, author, img, intro) VALUES (%s,%s,%s,%s)"
            # self.cur.execute(SQL, (title, author, img, intro))
            self.cur.execute(SQL)
            self.db.commit()

    def run(self):
        request = self.build_request(self.start_url)
        content = self.parse_request(request)
        content_list = self.parse_content(content)
        self.save_content(content_list)
        self.cur.close()
        self.db.close()


if __name__ == '__main__':
    for i in range(1,11):
        a = ZonghengSpider("http://www.zongheng.com/rank/details.html?rt=1&d=1&i=2&p={}".format(i))
        a.run()
