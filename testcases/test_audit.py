import unittest
import os
import jsonpath
from library.ddt import ddt, data
from common.readexcel import ReadExcel
from common.handlepath import DATADIR
from common.handleconfig import conf
from common.handlerequest import SendRequests
from common.handlelog import log
from common.handledata import CaseData, replace_data
from common.connectdb import DB

file_path = os.path.join(DATADIR, "api_cases_excel")
"""
审核步骤
登录（所有审核用例执行之前，登录就可以）
加标（每一个用例执行之前都要加标）
审核
"""

file_path = os.path.join(DATADIR, "api_cases_excel.xlsx")


@ddt
class TestAudit(unittest.TestCase):
    excel = ReadExcel(file_path, "loan_audit")
    cases = excel.read_data()
    request = SendRequests()
    db = DB()

    @classmethod
    def setUpClass(cls) -> None:
        """进行登录"""
        # 准备登录数据
        url = conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": conf.get("test_data", "admin_phone"),
            "pwd": conf.get("test_data", "admin_pwd")
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
        CaseData.admin_member_id = str(jsonpath.jsonpath(res, "$..id")[0])

    def setUp(self) -> None:
        """进行加标"""
        # 1、准备加标数据
        url = conf.get("env", "url") + '/loan/add'
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = CaseData.token_value
        data = {"member_id": CaseData.admin_member_id,
                "title": "报名 Java 全栈自动化课程",
                "amount": 1000,
                "loan_rate": 12.0,
                "loan_term": 12,
                "loan_date_type": 1,
                "bidding_days": 5}
        # 发送请求：添加项目
        response = self.request.send(url=url, method="post", json=data, headers=headers)
        res = response.json()
        # 提取审核需要用到的项目id
        CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])

    @data(*cases)
    def test_audit(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        data = eval(replace_data(case["data"]))
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = CaseData.token_value
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        response = self.request.send(url=url, method=method, json=data, headers=headers)
        res = response.json()
        if res["code"] == 0 and case["title"] == "审核项目成功-审核通过":
            CaseData.pass_loan_id = str(data["loan_id"])

        # 第三步：断言 对比预期结果和实际结果
        try:
            self.assertEqual(expected["code"], res["code"])
            self.assertEqual(expected["msg"], res["msg"])
            # 判断是否需要进行sql校验
            if case["check_sql"]:
                sql = replace_data(case["check_sql"])
                status = self.db.find_one(sql)["status"]
                # 断言数据库中的标状态是否和预期一致
                self.assertEqual(expected["status"], status)
        except AssertionError as e:
            print("预期结果", expected)
            print("实际结果", res)
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{},执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))
