import pymysql
from common.handleconfig import conf


class DB:
    def __init__(self):
        # 创建了解对象
        self.conn = pymysql.connect(host=conf.get("db", "host"),
                                    port=conf.getint("db", "port"),
                                    user=conf.get("db", "user"),
                                    password=conf.get("db", "pwd"),
                                    charset=conf.get("db", "charset"),
                                    # 通过设置游标类型，可以控制查询出来的数据类型
                                    cursorclass=pymysql.cursors.DictCursor
                                    )
        # 第二步：创建一个游标对象
        self.cur = self.conn.cursor()

    # 获取查询出来的第一条语句
    def find_one(self, sql):
        # 执行查询语句
        self.conn.commit()
        self.cur.execute(sql)
        data = self.cur.fetchone()
        return data

    # 获取查询出来的所有语句
    def find_all(self, sql):
        self.conn.commit()
        self.cur.execute(sql)
        data = self.cur.fetchall()
        return data

    # 查询数据的条数
    def find_count(self, sql):
        self.conn.commit()
        return self.cur.execute(sql)

    # 先关闭游标，再断开连接
    def close(self):
        self.cur.close()
        self.conn.close()
