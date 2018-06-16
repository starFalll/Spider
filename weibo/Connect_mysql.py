#连接数据库
from sqlalchemy import create_engine
from yaml import load

#加载配置
def loadconf_db(file_path):
    with open(file_path,'r',encoding='utf-8') as f:
            cont=f.read()
            cf=load(cont)
            return cf

def Connect(file):
    conf = loadconf_db(file)
    db = conf.get('db')
    connect_str = 'mysql+pymysql://' + str(db['user']) + ':' + str(db['password']) + '@127.0.0.1:3306/weibo?charset=utf8mb4'
    engine = create_engine(connect_str, encoding='utf-8')
    return conf,engine