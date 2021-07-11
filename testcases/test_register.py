import unittest
import os
import random
from library.ddt import ddt, data
from common.readexcel import ReadExcel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequest import SendRequests
from common.handlelog import log
from common.connectdb import DB


@ddt
class TestRegister(unittest.TestCase):
    excel = ReadExcel(os.path.join(DATADIR, "api_cases_excel.xlsx"), "register")
    cases = excel.read_data()
    request = SendRequests()
    db = DB()

    @data(*cases)
    def test_register(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        # 生产手机号
        phone = self.random_phone()
        # 替换测试用例数据中的手机号码
        case["data"] = case["data"].replace("#phone#", phone)
        data = eval(case["data"])
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        response = self.request.send(url=url, method=method, json=data, headers=headers)
        res = response.json()
        # 第三步：断言 对比预期结果和实际结果
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            if case["check_sql"]:
                sql = "SELECT * FROM futureloan.member WHERE mobile_phone={}".format(data["mobile_phone"])
                count = self.db.find_count(sql)
                self.assertEqual(1, count)
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{},执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))

    def random_phone(self):
        phone = "136"
        n = random.randint(100000000, 999999999)
        phone += str(n)[1:]
        # for i in range(8):
        #     n = random.randint(1, 9)
        #     phone += str(n)
        return phone


@ddt
class TestLogin(unittest.TestCase):
    excel = ReadExcel(os.path.join(DATADIR, "api_cases_excel.xlsx"), "login")
    cases = excel.read_data()
    request = SendRequests()

    @data(*cases)
    def test_login(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        data = eval(case["data"])
        headers = eval(conf.get("env", "headers"))
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        response = self.request.send(url=url, method=method, json=data, headers=headers)
        res = response.json()
        # 第三步：断言 对比预期结果和实际结果
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{},执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))
