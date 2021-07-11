import unittest
import os
import random
import jsonpath
from library.ddt import ddt, data
from common.readexcel import ReadExcel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequest import SendRequests
from common.handlelog import log
from common.connectdb import DB
from decimal import Decimal
from common.handledata import CaseData, replace_data


@ddt
class TestRecharge(unittest.TestCase):
    excel = ReadExcel(os.path.join(DATADIR, "api_cases_excel.xlsx"), "recharge")
    cases = excel.read_data()
    request = SendRequests()
    db = DB()

    # 测试用例类执行之前执行
    @classmethod
    def setUpClass(cls):
        # 准备登录数据
        url = conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": conf.get("test_data", "phone"),
            "pwd": conf.get("test_data", "pwd")
        }
        headers = eval(conf.get("env", "headers"))
        # 发送请求进行登录
        response = cls.request.send(url=url, method="post", json=data, headers=headers)
        # 获取返回的数据
        res = response.json()
        # 提取token,保存为类属性
        token = jsonpath.jsonpath(res, "$..token")[0]
        token_type = jsonpath.jsonpath(res, "$..token_type")[0]
        # 将提取的token设为类属性
        CaseData.token_value = token_type + " " + token
        # 提取用户id保存为类属性
        CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])

    @data(*cases)
    def test_recharge(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        # 替换参数中的member_id
        case["data"] = replace_data(case["data"])
        data = eval(case["data"])
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = CaseData.token_value
        # 在入请求头中加入setupclass中提取出来的token
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        # 发送请求前获取用户余额
        if case["check_sql"]:
            sql = "SELECT leave_amount FROM futureloan.member WHERE mobile_phone={}".format(
                conf.get("test_data", "phone"))
            # 查询当前用户的余额
            start_amount = self.db.find_one(sql)["leave_amount"]

        response = self.request.send(url=url, method=method, json=data, headers=headers)
        res = response.json()
        # 发送请求后获取用户余额
        if case["check_sql"]:
            sql = "SELECT leave_amount FROM futureloan.member WHERE mobile_phone={}".format(
                conf.get("test_data", "phone"))
            # 查询当前用户的余额
            end_amount = self.db.find_one(sql)["leave_amount"]
        # 第三步：断言 对比预期结果和实际结果
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 判读是否需要进行sql校验
            if case["check_sql"]:
                self.assertEqual(end_amount - start_amount, Decimal(str(data["amount"])))
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{},执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))
# @ddt
# class TestRecharge(unittest.TestCase):
#     excel = ReadExcel(os.path.join(DATADIR, "api_cases_excel.xlsx"), "recharge")
#     cases = excel.read_data()
#     request = SendRequests()
#     db = DB()
#
#     # 测试用例类执行之前执行
#     @classmethod
#     def setUpClass(cls):
#         # 准备登录数据
#         url = conf.get("env", "url") + "/member/login"
#         data = {
#             "mobile_phone": conf.get("test_data", "phone"),
#             "pwd": conf.get("test_data", "pwd")
#         }
#         headers = eval(conf.get("env", "headers"))
#         # 发送请求进行登录
#         response = cls.request.send(url=url, method="post", json=data, headers=headers)
#         # 获取返回的数据
#         res = response.json()
#         # 提取token,保存为类属性
#         token = jsonpath.jsonpath(res, "$..token")[0]
#         token_type = jsonpath.jsonpath(res, "$..token_type")[0]
#         # 将提取的token设为类属性
#         cls.token_value = token_type + " " + token
#         # 提取用户id保存为类属性
#         cls.member_id = jsonpath.jsonpath(res, "$..id")[0]
#
#     @data(*cases)
#     def test_recharge(self, case):
#         # 第一步：准备用例数据
#         url = conf.get("env", "url") + case["url"]
#         method = case["method"]
#         # 替换参数中的member_id
#         case["data"] = case["data"].replace("#member_id#", str(self.member_id))
#         data = eval(case["data"])
#         headers = eval(conf.get("env", "headers"))
#         headers["Authorization"] = self.token_value
#         # 在入请求头中加入setupclass中提取出来的token
#         expected = eval(case["expected"])
#         row = case["case_id"] + 1
#         # 第二步：发送请求，获取结果
#         # 发送请求前获取用户余额
#         if case["check_sql"]:
#             sql = "SELECT leave_amount FROM futureloan.member WHERE mobile_phone={}".format(
#                 conf.get("test_data", "phone"))
#             # 查询当前用户的余额
#             start_amount = self.db.find_one(sql)["leave_amount"]
#
#         response = self.request.send(url=url, method=method, json=data, headers=headers)
#         res = response.json()
#         # 发送请求后获取用户余额
#         if case["check_sql"]:
#             sql = "SELECT leave_amount FROM futureloan.member WHERE mobile_phone={}".format(
#                 conf.get("test_data", "phone"))
#             # 查询当前用户的余额
#             end_amount = self.db.find_one(sql)["leave_amount"]
#         # 第三步：断言 对比预期结果和实际结果
#         try:
#             self.assertEqual(expected["code"], res["code"])
#             self.assertEqual(expected["msg"], res["msg"])
#             # 判读是否需要进行sql校验
#             if case["check_sql"]:
#                 self.assertEqual(end_amount - start_amount, Decimal(str(data["amount"])))
#         except AssertionError as e:
#             self.excel.write_data(row=row, column=8, value="未通过")
#             log.error("用例：{},执行未通过".format(case["title"]))
#             log.exception(e)
#             raise e
#         else:
#             self.excel.write_data(row=row, column=8, value="通过")
#             log.info("用例：{}，执行通过".format(case["title"]))
