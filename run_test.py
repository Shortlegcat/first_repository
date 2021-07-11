import unittest
import os
from common.handlepath import CASEDIR, REPORTDIR
from HTMLTestRunnerNew import HTMLTestRunner
from common.handleemail import send_email

# 第一步创建套件
suite = unittest.TestSuite()
# 第二步加载用例到套件
loader = unittest.TestLoader()
print(CASEDIR)
suite.addTest(loader.discover(CASEDIR))
# 第三步：执行用例
report_file = os.path.join(REPORTDIR, "report1.html")
runner = HTMLTestRunner(stream=open(report_file, "wb"),
                        description="第一次接口测试报告",
                        title="py25测试报告",
                        tester="smz")
runner.run(suite)
send_email(report_file, "臭傻明")
