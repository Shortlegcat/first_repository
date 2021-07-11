import os

# 获取当前文件绝对路径

# 项目目录路径
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASEDIR)
# 用例模块目录路径
CASEDIR = os.path.join(BASEDIR, "testcases")

# 用例数据目录路径
DATADIR = os.path.join(BASEDIR, "data")

# 测试报告目录路径
REPORTDIR = os.path.join(BASEDIR, "reports")

# 配置文件目录的路径
CONFDIR = os.path.join(BASEDIR, "conf")

# 日志文件目录的路径
LOGDIR = os.path.join(BASEDIR, "logs")

