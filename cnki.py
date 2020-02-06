"""
1, 知网爬虫（2020-2-3）
2, 明确爬取目标：根据输入的关键词进行检索（python)
    title : 题名
    Author: 作者
    origin: 来源
    pub_date: 发表时间
    database: 数据库
    count: 下载次数
3, start_url: https://www.cnki.net/
   selenium 输入相关的词语获取资源页面;
   提取数据，返回数据；
   保存数据；
   获取下一页的button，重复提取数据和保存数据；
   关闭driver
"""

from selenium import webdriver
import time
import xlwt   # 操作excel


class Cnki(object):
    """知网爬虫"""

    # 类型注释            参数1    字符串   参数2  整数
    def __init__(self, keywords: str = None, depth: int = None):
        """
        初始化webdriver,和excel 工作簿， start_url，传入关键词和爬取的页数
        :param keywords: 关键词
        :param depth: 爬取的页数（默认从1开始）
        """
        self.keywords = keywords
        self.depth = depth
        self.driver = webdriver.Chrome(executable_path="/Users/lxf/Desktop/driver/chromedriver")
        self.start_url = "https://www.cnki.net/"
        self.book = xlwt.Workbook()


    def input_key_search(self):
        """关键词搜索，到达相关页面, 进入iframe"""
        self.driver.get(self.start_url)
        # 去除首页展示视频
        # self.driver.find_element_by_xpath("//span[@class='layui-layer-setwin']").click()
        # 输入关键字进行查看
        self.driver.find_element_by_class_name("search-input").send_keys(self.keywords)
        # 进入搜索页
        self.driver.find_element_by_class_name("search-btn").click()

        # 进入iframe
        frame = self.driver.find_element_by_id("iframeResult")
        self.driver.switch_to.frame(frame)




    def get_content(self):
        """提取返回相关数据"""

        # 获取tr 列表
        tr_list = self.driver.find_elements_by_xpath("//table[@class='GridTableContent']/tbody/tr")
        tr_list = tr_list[1:]

        item = {}

        for tr in tr_list:
            """
            展示隐藏的作者名字
            try:
                tr.find_element_by_xpath("./td[@class='author_flag']/a[@class='showAll']").click()
            except Exception:
                pass
            与进入下一页存在冲突
            """

            # 标题
            item["title"] = tr.find_element_by_xpath(".//td[2]/a").text
            author_list = tr.find_elements_by_xpath(".//td[@class='author_flag']/a[@class='KnowledgeNetLink']")
            # 作者
            author = []
            if author_list:
                for each in author_list:
                    author.append(each.text)
            else:
                author.append(tr.find_element_by_xpath(".//td[@class='author_flag']").text)
            item["author"] = " ".join(author)
            # 来源
            try:
                origin = tr.find_element_by_xpath(".//td[4]/a").text
            except Exception as e:
                origin = tr.find_element_by_xpath(".//td[4]").text

            item["origin"] = origin

            # 发表时间
            item["pub_date"] = tr.find_element_by_xpath(".//td[5]").text

            # 数据库
            item["database"] = tr.find_element_by_xpath(".//td[6]").text

            # 下载次数
            try:
                count = tr.find_element_by_xpath(".//td[8]/span/a").text
            except Exception:
                count = 0
            item["count"] = count
            yield item

        # self.driver.switch_to.default_content()

    def to_next_page(self):
        """进入下一页"""

        try:
            self.driver.find_element_by_link_text("下一页").click()
            print("成功进入下一页")
        except Exception:
            print("进入下一页错误")



    def save_item(self, items, page_num):
        """保存数据"""

        # 添加工作页：sheet
        sheet = self.book.add_sheet('知网%d' %page_num)

        i = 0
        while i < 20:
            for item in items:
                    for index, value in enumerate(item.values()):
                        sheet.write(i, index, value)
                    i += 1

        # 工作簿命名： 知网.xlsx
        self.book.save("知网.xls")

    def run(self):
        """实现主要爬取逻辑"""

        # 1, 输入关键字发起请求，到达相关页面
        self.input_key_search()

        for i in range(1, 5):
            # 2, 提取,返回相关数据
            item = self.get_content()
            # 3, 保存数据
            self.save_item(item, i)
            # 4, 进入下一页，循环2， 3
            self.to_next_page()
            time.sleep(2)

        # 退出浏览器
        self.driver.quit()

if __name__ == "__main__":
    ck = Cnki("python", 4)
    ck.run()

