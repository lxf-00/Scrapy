# 爬取豆瓣top250电影   使用requests模块（python3)

""" 一，确定爬取的内容
    1, movie_title: 电影名字
    2, pub_date: 发布年份
    3, area: 地区
    4， rating_num : 评分
    5， img: 展示图片
    6, comment_num: 评论数（多少人评价）
    7, type: 类型

    二，确定url(包含所有信息资源)，发起请求（headers, proxies)
    start_url   https://movie.douban.com/top250?start=0&filter=    第一页
    second_url  https://movie.douban.com/top250?start=25&filter=   第二页
    url_temp =  ["https://movie.douban.com/top250?start={}".format(i) for i in range(250) if i % 25 == 0]
    总共10页，每25部电影为一页

    三， 确定所需资源具体位置,提取所需内容（lxml.etree处理网页内容, re正则表达式， strip() 去除首尾空格）
    ol[@class=grid_view]//li

    四， 保存设置
    保存到当前路径下豆瓣t250.txt

    五，代码实现
"""

import requests
from lxml import etree
import time
import random
import re
import json


class DouBan():
    """ 爬取豆瓣t250电影"""

    def __init__(self):
        """初始化"""

        # 添加headers: 字典格式
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"}

        # url 列表
        self.url_list = ["https://movie.douban.com/top250?start={}".format(i) for i in range(250) if i % 25 == 0]

        # proxies
        self.proxies = {
            "http": "http://223.199.24.196:9999",
            "http": "http://115.216.59.3:9999"
        }


    def parse_url(self, url_list):
        """循环发起请求，保存反应内容
        :param url_list   url列表
        :return  html_list   处理后的html内容列表
        """

        # 用于保存html
        html_list = []

        for url in url_list:
            # 停留随机0~ 1 秒
            time.sleep(round(random.uniform(0, 1), 2))
            response = requests.get(url, headers=self.headers, proxies=self.proxies)
            html = response.content.decode()
            html = etree.HTML(html)
            html_list.append(html)


        # 返回内容列表
        return html_list

    def get_content(self, html_list):
        """
        查找相应的内容
        :param html_list:
        :return: 所需内容的字典 用于接下来的保存
        """
        # 用于保存所有内容的字典
        item = {}
        for html in html_list:
            li_list = html.xpath("//ol[@class='grid_view']/li")
            for li in li_list:
                item["movie_title"] = li.xpath(".//div[@class='hd']/a/span[1]/text()")[0]
                item["pub_date"] = re.findall(r'(\d+)', str(li.xpath(".//div[@class='bd']/p[1]/text()")))[3]
                #                             将列表转为字符串         地区信息内容                           去除首尾空白
                area = re.split(r'\n', "".join(li.xpath(".//div[@class='bd']/p[1]/text()")))[2].strip()
                """
                1991 / 美国 法国 / 犯罪 剧情 惊悚
                1997 / 美国 / 动作 科幻 犯罪 惊悚
                2007 / 美国 / 剧情 科幻
                """
                # 获取排在第一位的地区（称之为主要地区吧）
                item["area"] = re.split(r'/', area)[1].strip()
                # 获取主要类型
                item["type"] = re.split(r'/', area)[2].strip()
                item["rating_num"] = "".join(li.xpath(".//span[@class='rating_num']/text()"))
                item["comment_num"] = re.match(r'(\d+)', li.xpath(".//div[@class='star']/span[4]/text()")[0]).group()

                item["img"] = li.xpath(".//div[@class='pic']/a/img/@src")[0]


                # 使用生成器返回item
                yield item


    def save_content(self, item):
        """
        保存数据
        :param item: 数据   生成器
        :return: None
        """


        # 保存在当前文件下            追加写入
        with open("./豆瓣t250.txt", 'a') as f:
            # 生成器需要遍历
            for each in item:
                # item 是字典类型，写入txt文档会报错，先使用json.dumps转化为字符串类型
                content = json.dumps(each, ensure_ascii=False)
                f.write(content)
                f.write("\n")


    def run(self):
        """实现主要逻辑"""
        # 发起请求，获取反应内容，同时使用etree处理html
        html_list = self.parse_url(self.url_list)

        # 获取相应的内容
        item = self.get_content(html_list)

        # 保存数据
        self.save_content(item)



if __name__ == "__main__":
    db = DouBan()
    db.run()




