""""
封装需求：
1、读取数据
2、写入数据
封装目的：
1、提高代码的重用率
封装的时候有哪些数据需要参数化
1、excel文件名
2、表单名
"""

import openpyxl


class ReadExcel(object):
    def __init__(self, filename, sheet_name):
        # 设置对象属性是为了在其他方法里用
        self.filename = filename
        self.sheet_name = sheet_name

    def open(self):
        # 读取excel文件 返回一个workbook工作簿对象
        self.wb = openpyxl.load_workbook(self.filename)
        # 选择表单
        self.sh = self.wb[self.sheet_name]

    def read_data(self):
        self.open()
        # 按照获取表格中所有格子的额数据 每一个行数据放在一个元祖中
        datas = list(self.sh.rows)
        # 获取第一行数据最为字典的键
        title = [i.value for i in datas[0]]
        cases = []
        for i in datas[1:]:
            values = [c.value for c in i]
            # print(values)
            case = dict(zip(title, values))
            # print(case)
            cases.append(case)
        return cases

    # 写入数据
    def write_data(self, row, column, value):
        self.open()
        # 写入数据
        self.sh.cell(row=row, column=column, value=value)
        # 保存数据
        self.wb.save(self.filename)
