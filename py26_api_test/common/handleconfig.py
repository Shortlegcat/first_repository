"""
封装目的：使用更简单
封装需求：
简化创建配置文件解析器对象，加载配置文件的流程（需要封装）,提示重写init方法
读取数据（不进行封装，使用原来的方法--通过继承）
简化写入数据的操作（需要封装）自定义一个 write_data方法
"""
import os
from configparser import ConfigParser
from common.handlepath import CONFDIR


class HandleConfig(ConfigParser):
    def __init__(self, filename):
        super().__init__()
        # 调用父类的init方法
        self.filename = filename
        self.read(filename, encoding="utf8")

    def write_data(self, section, options, value):
        self.set(section, options, value)
        self.write(fp=open(self.filename, "w"))


conf = HandleConfig(os.path.join(CONFDIR, "config.ini"))
