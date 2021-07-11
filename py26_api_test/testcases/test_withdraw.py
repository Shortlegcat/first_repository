import unittest
import os
import jsonpath
from library.ddt import ddt, data
from common.readexcel import ReadExcel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequest import SendRequests
from common.handlelog import log
from common.connectdb import DB
from decimal import Decimal

file_path = os.path.join(DATADIR, "api_cases_excel.xlsx")


@ddt
class TestWithdraw(unittest.TestCase):
    excel = ReadExcel(file_path, "withdraw")
    cases = excel.read_data()
    request = SendRequests()
    db = DB()

    @data(*cases)
    def test_withdraw(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        case["data"] = case["data"].replace("#phone#", conf.get("test_data", "phone"))
        case["data"] = case["data"].replace("#pwd#", conf.get("test_data", "pwd"))
        headers = eval(conf.get("env", "headers"))
        if case["interface"].lower() == "withdraw":
            headers["Authorization"] = self.token_value
            case["data"] = case["data"].replace("#member_id#", str(self.member_id))
        data = eval(case["data"])
        expected = eval(case["expected"])
        method = case["method"]
        row = case["case_id"] + 1
        # 判断是否需要进行sql校验
        if case["check_sql"]:
            sql = case["check_sql"].format(conf.get("test_data", "phone"))
            start_money = self.db.find_one(sql)["leave_amount"]
        # 第二步：调用接口，获取实际结果
        response = self.request.send(url=url, method=method, json=data, headers=headers)
        res = response.json()
        if case["interface"].lower() == "login":
            # 提取用户id,token保存为类属性
            TestWithdraw.member_id = jsonpath.jsonpath(res, "$..id")[0]
            token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            TestWithdraw.token_value = token_type + " " + token

        # 第三步：断言
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            if case["check_sql"]:
                sql = case["check_sql"].format(conf.get("test_data", "phone"))
                end_money = self.db.find_one(sql)["leave_amount"]
                # 比对取现金额是否正确
                self.assertEqual(Decimal(str(data["amount"])), start_money - end_money)
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{},执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))
