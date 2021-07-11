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

"""
投资接口
1、需要标：管理员登录、加标、审核
2、用户登录
3、审核
4、关于投资的sql语句校验
    用户表、校检用户余额是否发生变化，变化金额等于所投金额（根据用户id去查member表
    根据用户id和 标id去投资表中查用户的投资记录，（invest表里
    根据用户id去流水表中查询流水记录（查询用户投资之后是否多了一条记录

"""
file_path = os.path.join(DATADIR, "api_cases_excel.xlsx")


@ddt
class TestInvest(unittest.TestCase):
    excel = ReadExcel(file_path, "invest")
    cases = excel.read_data()
    request = SendRequests()

    @data(*cases)
    def test_invest(self, case):
        # 第一步：准备用例数据
        url = conf.get("env", "url") + case["url"]
        method = case["method"]
        data = eval(replace_data(case["data"]))
        headers = eval(conf.get("env", "headers"))
        # 判断是否是登录接口，不是登录接口则需要添加token
        if case["interface"] != "login":
            headers["Authorization"] = CaseData.token_value
        expected = eval(case["expected"])
        row = case["case_id"] + 1
        # 第二步：发送请求，获取结果
        response = self.request.send(url=url, method=method, json=data, headers=headers)
        res = response.json()
        if case["interface"] == "login":
            # 提取token,保存为类属性
            token = jsonpath.jsonpath(res, "$..token")[0]
            token_type = jsonpath.jsonpath(res, "$..token_type")[0]
            # 将提取的token设为类属性
            CaseData.token_value = token_type + " " + token
            # 提取用户id保存为类属性
            CaseData.member_id = str(jsonpath.jsonpath(res, "$..id")[0])
        # 判断是否加标的用例，如果是则添加id
        if case["interface"] == "loan_add":
            CaseData.loan_id = str(jsonpath.jsonpath(res, "$..id")[0])
        # 判断是否加标的用例，如果是则添加id
        # 第三步：断言 对比预期结果和实际结果
        try:
            self.assertEqual(expected["code"], res["code"])
            # self.assertEqual(expected["msg"], res["msg"])
            self.assertIn(expected["msg"], res["msg"])
        except AssertionError as e:
            self.excel.write_data(row=row, column=8, value="未通过")
            log.error("用例：{},执行未通过".format(case["title"]))
            log.exception(e)
            raise e
        else:
            self.excel.write_data(row=row, column=8, value="通过")
            log.info("用例：{}，执行通过".format(case["title"]))
