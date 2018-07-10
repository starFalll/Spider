"""
@author:ACool(www.github.com/starFalll)
删除不在conf.yaml配置文件中的微博用户及其动态
"""
from sqlalchemy import MetaData, Table, select

from weibo.Connect_mysql import Connect


def DeleteUsers():
    conf, engine = Connect('conf.yaml')
    conn = engine.connect()
    metadata = MetaData(engine)
    wb_data = Table('wb_data', metadata, autoload=True)
    wb_user = Table('wb_user', metadata, autoload=True)
    wb_topic = Table('wb_topic', metadata, autoload=True)
    empty = select([wb_user.c.uid])
    res = conn.execute(empty)  # 得到WBUser表中所有的uid
    deluid = []  # 要删除的uid
    uids = conf.get('uids')
    uids = list(uids.values())  # 得到配置文件中的uid
    for r in res:
        if (int(r[0]) not in uids):
            deluid.append(r[0])
    for uid in deluid:
        exc = wb_data.delete().where(wb_data.c.uid == str(uid))  # 删除用户动态信息
        conn.execute(exc)
        exc = wb_topic.delete().where(wb_topic.c.uid == str(uid))  # 删除用户主题
        conn.execute(exc)
        exc = wb_user.delete().where(wb_user.c.uid == str(uid))  # 删除用户个人信息
        conn.execute(exc)

    conn.close()


if __name__ == '__main__':
    DeleteUsers()
