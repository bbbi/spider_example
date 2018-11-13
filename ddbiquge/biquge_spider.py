# -*- coding: utf-8 -*-
from queue import Queue
from threading import Thread
from urllib import request, parse

from lxml import etree

from utils.get_ua import get_pc


class BiqugeSpider:
    def __init__(self, start_url):
        self.start_url = start_url  # 起始url
        self._request = Queue()
        self._content = Queue()
        self.headers = {
            "Host": "www.ddbiquge.com",
            "User-Agent": get_pc()
        }

    def build_request(self, start_url):
        list_request = request.Request(start_url, headers=self.headers)  # 构建列表页请求
        list_response = request.urlopen(list_request)  # 请求列表页
        list_content = list_response.read()
        # 解析列表页并构建详情页请求
        lxml_content = etree.HTML(list_content)  # lxml化响应
        a_list = lxml_content.xpath("//div[@class='listmain']/dl/dd/a")[9:]  # 取正文a标签
        # print("目录解析完成")
        for a in a_list:
            # print(a.xpath("./@href")[0])
            detail_url = parse.urljoin(self.start_url, a.xpath("./@href")[0])  # 取详情页url
            detail_request = request.Request(detail_url, headers=self.headers)
            self._request.put(detail_request)
        print(self._request.qsize())

    def parse_request(self):
        while True:
            detail_request = self._request.get()  # 获取一个详情页请求对象
            detail_response = request.urlopen(detail_request)  # 请求详情页
            detail_lxml = etree.HTML(detail_response.read())  # lxml化相应
            title = detail_lxml.xpath("//div[@class='content']/h1/text()")[0]
            content_list = detail_lxml.xpath("//div[@class='showtxt']//text()")
            _temp = []
            for con in content_list:
                # con = re.sub(r"\\xa0", '', con)
                _temp.append(con)

            content = ''.join(_temp)
            print(title)
            self._content.put({title: content})
            self._request.task_done()

    def save_content(self):
        while True:
            content = self._content.get()
            for k, v in content.items():
                with open('E:\spider\\A\\ddbiquge\\jianlai\\{}.txt'.format(k), 'w', encoding='utf-8') as f:
                    f.write(k)
                    f.write('\n')
                    f.write(v)

            self._content.task_done()

    def run(self):
        t_list = []
        self.build_request(self.start_url)  # 开始解析目录页
        for i in range(5):
            print('解析线程' + str(i))
            t = Thread(target=self.parse_request)
            t_list.append(t)

        for i in range(2):
            print('保存线程' + str(i))
            t1 = Thread(target=self.save_content)
            t_list.append(t1)

        for i in t_list:
            i.setDaemon(True)
            i.start()

        for q in [self._content, self._request]:
            q.join()


if __name__ == '__main__':
    jianlai = BiqugeSpider("https://www.ddbiquge.com/book/44455.html")
    jianlai.run()
