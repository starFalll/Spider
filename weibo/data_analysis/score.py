from weibo.Connect_mysql import Connect
from sqlalchemy import MetaData, Table, select
import sys

def cul_score(uid):
    if(len(sys.argv)==2):
        uid=sys.argv[1]
    _, engine = Connect('../conf.yaml')  # 连接数据库
    conn = engine.connect()
    metadata = MetaData(engine)
    wb_user = Table('wb_user', metadata, autoload=True)
    s = select([wb_user]).where(wb_user.c.uid == uid)
    res = conn.execute(s)
    conn.close()
    score=100
    for row in res:
        for info in row[1:]:
            if(info==''):
                score-=10
    print(score)

if __name__ == '__main__':
    conf, _ = Connect('../conf.yaml')
    uid = conf.get('uids')
    uid = list(uid.values())[0]
    cul_score(uid)  # 指定需要分析的用户的uid（必须先存在conf.yaml里面，并且运行了一次sina_spider程序），默认为conf.yaml中的第一条uid