#! /usr/bin python3

#创建数据库的代码：
"""
CREATE DATABASE BaiduResult;
USE BaiduResult;
CREATE TABLE KeyWords
(KeywordID int PRIMARY KEY AUTO_INCREMENT,
 Keyword varchar(50) NOT NULL ,
 Word varchar(50) NOT NULL
)DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE KeywordsLinks
(LinkID int PRIMARY KEY AUTO_INCREMENT,
 Link varchar(500) NOT NULL,
 Content text NULL,
 KeyWordID int NOT NULL,
 FOREIGN KEY(KeywordID)
 REFERENCES KeyWords(KeywordID)
 ON UPDATE CASCADE
 ON DELETE CASCADE
)DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
"""

# mysql> describe KeyWords;
# +-----------+-------------+------+-----+---------+----------------+
# | Field     | Type        | Null | Key | Default | Extra          |
# +-----------+-------------+------+-----+---------+----------------+
# | KeywordID | int(11)     | NO   | PRI | NULL    | auto_increment |
# | Keyword   | varchar(50) | NO   |     | NULL    |                |
# | Word      | varchar(50) | NO   |     | NULL    |                |
# +-----------+-------------+------+-----+---------+----------------+



# mysql> describe  KeywordsLinks;
# +-----------+--------------+------+-----+---------+----------------+
# | Field     | Type         | Null | Key | Default | Extra          |
# +-----------+--------------+------+-----+---------+----------------+
# | LinkID    | int(11)      | NO   | PRI | NULL    | auto_increment |
# | Link      | varchar(500) | NO   |     | NULL    |                |
# | Content   | text         | YES  |     | NULL    |                |
# | KeyWordID | int(11)      | NO   | MUL | NULL    |                |
# +-----------+--------------+------+-----+---------+----------------+

import requests
import re
import time
import pymysql
import random



def find_keyword_web(cur):
    key_word_link={} #key_word_link:{key1:{aim1:{1:***,2:***,3:***},aim2:{***}},key2:{}}，1,2,3代表页数
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }
    pattern_link=re.compile(r'<h3 class="t">.*?href="(.*?)"',re.S)
    pattern_next_page=re.compile(r'下一页',re.S)
    pattern_front_page=re.compile(r'上一页',re.S)
    pattern_page_num_first=re.compile(r'id="page">(.*?)</p>',re.S)
    cur.execute("select * from KeyWords")
    fr=cur.fetchall()
    for line in fr:
        key=line[1]
        aim=line[2]
        id=line[0]
        key_word_link[id]={}
        print("aim:"+aim+"key:"+key)
        baseUrl = 'http://www.baidu.com/s'
        page=1
        data = {'wd': aim, 'pn': str(page - 1) + '0', 'tn': 'baidurt', 'ie': 'utf-8', 'bsst': '1'}
        first_page=requests.get(baseUrl,params=data,headers=headers)#先爬一页来分析结构
        next=Judge_next_page(first_page,pattern_next_page)#判断是否有下一页
        front=Judge_front_page(first_page,pattern_front_page)#判断是否有上一页
        page_num=Get_Page_Num(pattern_page_num_first,first_page,front,next)#提取出页数
        key_word_link[id][key]=Get_Result_pages(baseUrl,page_num,pattern_link,aim,headers)
    print(key_word_link)
    return key_word_link

#判断是否有下一页
def Judge_next_page(page,pattern_next_page):
    items=re.findall(pattern_next_page,page.text)
    if(len(items)==0):
        return False
    else:
        return True
#判断是否有上一页
def Judge_front_page(page,pattern_front_page):
    items = re.findall(pattern_front_page, page.text)
    if(len(items)==0):
        return False
    else:
        return True

#提取出搜索结果的页数
def Get_Page_Num(pattern_page_num_first,page,front,next):
    aim=re.compile(r'href="(.*?)"',re.S)
    item = re.findall(pattern_page_num_first, page.text)
    str=item[0]
    result=re.findall(aim,str)
    length=len(result)
    if(front==True) and (next==True):#多了一个链接
        length=length-1
    if(length==0):#只有一页
        length=1
    return length
#提取出一页的结果，其中result={aim:{1:***,2:***,3:***}}，1,2,3代表页数
def Get_Result_pages(baseUrl,page_num,pattern_link,aim,headers):
    result={}
    result[aim]=[]
    for i in range(page_num):
        data = {'wd': aim, 'pn': str(i) + '0', 'tn': 'baidurt', 'ie': 'utf-8', 'bsst': '1'}
        page = requests.get(baseUrl, params=data, headers=headers)
        items = re.findall(pattern_link, page.text)
        result[aim]=result[aim]+items
        time.sleep(1)
    return result

def write_to_file(link,cur):
    for keyID,Other in link.items():# KeywordID , Other(Link,Keyword,Word)
        for k,pages_v in Other.items(): # Keyword , other(Word , Link)
            for w,links in pages_v.items(): # Word , Link
                for link in links:
                    cur.execute('INSERT INTO KeywordsLinks(Link,KeyWordID) VALUES ("%s","%d")' % (pymysql.escape_string(link),keyID))
                    cur.connection.commit()

def get_keyword_sentence(cur):
    cur.execute("select * from KeywordsLinks")
    results = cur.fetchall()
    for result in results:
        try:
            print(result)
            link=result[1]
            LinkID=result[0]
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
            }

            cur.execute("select Word from KeyWords,KeywordsLinks where KeywordsLinks.KeyWordID= KeyWords.KeyWordID and KeywordsLinks.LinkID=(%d)" % int(LinkID))
            keyword=(cur.fetchone())[0]
            pattern=re.compile(r'.{5,20}'+keyword+r'.{5,20}',re.S)
            replace=re.compile(r'<.*?>')
            page = requests.get(link, headers=headers,timeout=1)
            page=replace.sub('',page.text)
            items=re.findall(pattern,page)
            con=""
            for item in items:
                con+=item

            print(LinkID)
            print(len(con))
            cur.execute("""UPDATE KeywordsLinks SET Content="%s" WHERE LinkID=%d""" % (pymysql.escape_string(con),LinkID))#escape_string将用户的输入进行转义，防止SQL注入
            cur.connection.commit()
            time.sleep(random.random())
        except Exception:
            pass
#删除表中的空值
def delete_empty(cur):
    cur.execute("DElETE FROM KeywordsLinks WHERE Content=''")


if __name__=='__main__':
    #连接数据库
    user = input("Please input your mysql user name:")
    password = input("Please input your mysql password:")
    conn = pymysql.connect(host='localhost', user=user, passwd=password, db='mysql', charset='utf8', port=3306)#默认为127.0.0.1本地主机
    cur = conn.cursor()
    cur.execute("USE BaiduResult")

    key_word_link=find_keyword_web(cur)
    write_to_file(key_word_link,cur)
    get_keyword_sentence(cur)
    delete_empty(cur)
    cur.close()
    conn.close()