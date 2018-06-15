from sqlalchemy import create_engine, MetaData,Table, Column, Integer, String, ForeignKey,TEXT
import os
import pymysql
from yaml import load
"""
创建数据库
Why use utf8mb4 ,not utf8
However, for MySQL versions 5.5.3 on forward, a new MySQL-specific encoding 'utf8mb4' has been introduced. 
The rationale for this new encoding is due to the fact that MySQL’s utf-8 encoding 
only supports codepoints up to three bytes instead of four.

微博里面的emoji表情超过了utf-8编码范围：
UTF-8是3个字节, 其中已经包括我们日常能见过的绝大多数字体. 但3个字节远远不够容纳所有的文字, 
所以便有了utf8mb4, utf8mb4是utf8的超集, 占4个字节, 向下兼容utf8. 我们日常用的emoji表情就是4个字节了.
使用utf8mb4要求：
MySQL数据库版本>=5.5.3
MySQL-python" version  >= 1.2.5
"""

def loadconf_db(file_path):
    with open(file_path,'r',encoding='utf-8') as f:
            cont=f.read()
            cf=load(cont)
            return cf

if __name__ == '__main__':
    conf = loadconf_db(os.path.abspath('conf.yaml'))  # 获取配置文件的内容
    db = conf.get('db')

    conn = pymysql.connect(host='localhost', user=db['user'], passwd=db['password'], db='mysql', charset='utf8mb4',
                                                   port=3306)  # 默认为127.0.0.1本地主机
    cur = conn.cursor()
    cur.execute("Create database weibo")
    cur.close()
    conn.close()
    connect_str='mysql+pymysql://'+db['user']+':'+db['password']+'@127.0.0.1:3306/weibo?charset=utf8mb4'
    engine = create_engine(connect_str, encoding='utf-8')
    metadata=MetaData()
    WBUser = Table('WBUser',metadata,
        Column('userID',Integer, primary_key=True, autoincrement=True),     #主键，自动添加
        Column("uid", String(20), unique=True,nullable=False),               #微博用户的uid
        Column("Uname", String(50), nullable=False),                         #昵称
        Column("Certified", String(50), default='', server_default=''),      #认证信息
        Column("Sex", String(200), default='', server_default=''),           #性别nullable=False
        Column("Relationship", String(20), default='', server_default=''),   #感情状况
        Column("Area", String(500), default='', server_default=''),          #地区
        Column("Birthday", String(50), default='', server_default=''),       #生日
        Column("Education_info", String(300), default='', server_default=''),#学习经历
        Column("Work_info", String(300), default='', server_default=''),     #工作经历
        Column("Description", String(2500), default='', server_default=''),   #简介
        mysql_charset='utf8mb4'
    )
    WBData = Table('WBData' , metadata,
        Column('dataID',Integer, primary_key=True, autoincrement=True),     #主键，自动添加
        Column('uid',String(20), ForeignKey(WBUser.c.uid),nullable=False),  #外键
        Column('weibo_cont',TEXT,default=''),                               #微博内容
        Column('create_time', String(200),unique=True),                      #创建时间
        mysql_charset='utf8mb4'
    )

    metadata.create_all(engine)