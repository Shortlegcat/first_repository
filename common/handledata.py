import re
from common.handleconfig import conf


class CaseData:
    """这个类专门用来保存，执行执行过程中提取出来给其他用例用用的数据，相当于环境变量容器"""
    pass


# def replace_data(s):
#     r1 = r"#(.+?)#"
#     # 根据是否匹配到要替换的数据来决定是否进去循环
#     while re.search(r1, s):
#         # 匹配一个需要替换的内容
#         res = re.search(r1, s)
#         # 获取替换的内容
#         data = res.group()
#         # 获取需要替换的字段
#         key = res.group(1)
#         try:
#             # 根据要替换的字典，去配置文件中找到对应的数据进行替换
#             s = s.replace(data, conf.get("test_data", key))
#         except Exception:
#             # 如果配置文件中找不到，报错了，这区CaseData的属性中找对应的值进行替换
#             s = s.replace(data, getattr(CaseData, key))
#     return s


def replace_data(s):
    r1 = r"#(.+?)#"
    while re.search(r1, s):
        res = re.search(r1, s)
        key = res.group(1)
        try:
            value = conf.get("test_data", key)
        except Exception:
            value = getattr(CaseData, key)
        finally:
            # 切记value要为字符串
            s = re.sub(r1, value, s, 1)
    return s


if __name__ == "__main__":
    pass
