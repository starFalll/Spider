"""
@author:ACool(www.github.com/starFalll)
删除不在conf.yaml配置文件中的微博用户及其动态
"""
from weibo.Connect_mysql import Connect
from sqlalchemy import create_engine, MetaData,Table, select ,delete

def DeleteUsers():
    conf,engine = Connect('conf.yaml')
    conn = engine.connect()
    metadata = MetaData(engine)
    WBData = Table('WBData', metadata, autoload=True)
    WBUser = Table('WBUser', metadata, autoload=True)
    empty = select([WBUser.c.uid])
    res = conn.execute(empty)#得到WBUser表中所有的uid
    deluid = []                #要删除的uid
    uids = conf.get('uids')
    uids = list(uids.values())#得到配置文件中的uid
    for r in res:
        if(int(r[0]) not in uids):
            deluid.append(r[0])
    for uid in deluid:
        exc = WBData.delete().where(WBUser.c.uid==str(uid)) #删除用户动态信息
        conn.execute(exc)
        exc = WBUser.delete().where(WBUser.c.uid==str(uid))#删除用户个人信息
        conn.execute(exc)


    conn.close()





if __name__ == '__main__':
    DeleteUsers()
