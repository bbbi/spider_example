# -*- coding: utf-8 -*-
import json
from queue import Queue
from pymongo import MongoClient
from requests import Request, Session
import time


class LagouPySpider:
    client = MongoClient()
    count = 0

    def __init__(self):
        self.collection = self.client['lagou']['python']
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            "Cookie": "_ga=GA1.2.141694918.1539146328; _gid=GA1.2.151926403.1539146328; user_trace_token=20181010123849-61effd61-cc46-11e8-ae56-525400f775ce; LGUID=20181010123849-61f00006-cc46-11e8-ae56-525400f775ce; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221665c455e0c57a-05b939d02aabea-5701732-1327104-1665c455e0d3af%22%2C%22%24device_id%22%3A%221665c455e0c57a-05b939d02aabea-5701732-1327104-1665c455e0d3af%22%7D; LG_LOGIN_USER_ID=c8cb52ff63a6980ddb22feb78d63cc4269c71700f2536ea9a30c908a720bcdb3; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; LGSID=20181011091808-8355ea9c-ccf3-11e8-bbb2-5254005c3644; index_location_city=%E5%8C%97%E4%BA%AC; JSESSIONID=ABAAABAAAIAACBI150A4355C8CD90D97C293C3D0251B2AE; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1539146328,1539220688,1539221915; _putrc=22044C109A6F0256123F89F2B170EADC; login=true; unick=%E5%AE%8B%E6%96%8C; gate_login_token=0e62eda3125d054ed2adf734bc78dd26dcf068dfe449eaeb1fc51bcd8a237882; TG-TRACK-CODE=search_code; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1539223502; LGRID=20181011100503-1151f150-ccfa-11e8-bbb2-5254005c3644; SEARCH_ID=952822bf8ff24886a3f03eaee1284971",
            "Referer": "https://www.lagou.com/jobs/list_python?city=%E5%8C%97%E4%BA%AC&cl=false&fromSearch=true&labelWords=&suginput=",
        }
        self.request = Queue()
        # self.content = Queue()
        self.data = {
            'first': 'true',
            'pn': '1',
            'kd': 'python',
        }
        self.s = Session()
        self.url = "https://www.lagou.com/jobs/positionAjax.json?city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false"

    def prepare_request(self):
        # 构建接下来的请求对象
        for i in range(1, 31):
            if i == 1:
                # 起始请求
                request = Request('POST', self.url, headers=self.headers, data=self.data)
            else:
                self.data['first'] = 'false',
                self.data['pn'] = str(i)
                request = Request('POST', self.url, headers=self.headers, data=self.data)
            prepped = self.s.prepare_request(request)  # 准备完毕的请求对象
            self.request.put(prepped)

    def send_request(self):

        prepped = self.request.get()  # 从队列中获取请求对象
        response = self.s.send(prepped)  # 发送请求获取相应
        content = response.content.decode()  # 获取相应并解码
        # print('解析成功')
        # self.content.put(content)
        # self.request.task_done()
        return content

    def parse_content(self, content):
        con_dict = json.loads(content)  # 格式化json字符串
        result_list = con_dict['content']['positionResult']['result']  # 获取工作列表页
        # print('截取数据')
        for result in result_list:
            self.collection.insert(result)
            # self.count += 1
            # print('*' * 10 + str(self.count) + '*' * 10)

    def run(self):
        # 构建请求对象
        self.prepare_request()
        while not self.request.empty():
            # 发送请求，获取相应
            content = self.send_request()
            # 解析并保存数据
            self.parse_content(content)


if __name__ == '__main__':
    start_time = time.time()
    python = LagouPySpider()
    end_time = time.time()
    python.run()
    print("时间：" + str(end_time - start_time))
