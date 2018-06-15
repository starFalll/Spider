from sqlalchemy import create_engine
from weibo.sina_spider import loadconf_db

def Connect(file):
    conf = loadconf_db(file)
    db = conf.get('db')
    connect_str = 'mysql+pymysql://' + db['user'] + ':' + db['password'] + '@127.0.0.1:3306/weibo?charset=utf8mb4'
    engine = create_engine(connect_str, encoding='utf-8')
    return engine