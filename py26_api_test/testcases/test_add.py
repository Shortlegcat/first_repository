import os
import unittest
import jsonpath
from common.readexcel import ReadExcel
from common.handlepath import DATADIR
from library.ddt import ddt, data
from common.handleconfig import conf
from common.handlerequest import SendRequests
from common.handledata import CaseData, replace_data
from common.handlelog import log

file_path = os.path.join(DATADIR, "api_cases_excel.xlsx")


@ddt
class TestAdd(unittest.TestCase):
    pass
    excel = ReadExcel(file_path, "loan_add")
    cases = excel.read_data()
    request = SendRequests()

    @classmethod
    def setUpClass(cls):
        """管理员登录"""
        url = conf.get("env", "url") + "/member/login"
        data = {
            "mobile_phone": conf.get("test_data", "admin_phone"),
            "pwd": conf.get("test_data", "admin_pwd")
        }
        headers = eval(conf.get("env", "headers"))
        response = cls.request.send(url=url, method="post", json=data, headers=headers)
        res = response.json()
        token = jsonpath.jsonpath(res, "$..token")[0]
        token_type = jsonpath.jsonpath(res, "$..token_type")[0]
        member_id = str(jsonpath.jsonpath(res, "$..id")[0])
        # 将提取的数据保存到CaseData的属性中
        CaseData.admin_token_value = token_type + " " + token
        CaseData.admin_member_id = member_id

    @data(*cases)
    def test_add(self, case):
        # 第一步：准备数据
        url = conf.get("env", "url") + case["url"]
        headers = eval(conf.get("env", "headers"))
        headers["Authorization"] = CaseData.admin_token_value
        data = eval(replace_data(case["data"]))
        expected = eval(case["expected"])
        method = case["method"]
        row = case["case_id"]

        # 第二步：发送请求获取实际结果
        response = self.request.send(url=url, method="post", json=data, headers=headers)
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
