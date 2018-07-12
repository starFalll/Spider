import pickle
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.mysql import insert
from selenium import webdriver
from weibo.Connect_mysql import Connect
import re
import time
import random
import pymysql
import datetime


def getinfo(conn, driver, uid, table):
    time.sleep(2)
    driver.get('https://weibo.com/p/100505' + str(uid) + '/info?mod=pedit_more')  # 资料页
    time.sleep(5)


    '''
    正则表达式组
    '''
    info = re.compile(r'<span class="pt_title S_txt2"(.*?)</li>', re.S)  # 信息
    information = re.compile(r'>(.*?)：', re.S)  # 匹配信息名称字段
    content = re.compile(r'class="pt_detail">(.*?)</span>', re.S)  # 内容
    job = re.compile(r'loc=infjob" target="_blank">(.*?)</a>', re.S)  # 工作信息
    edu = re.compile(r'loc=infedu">(.*?)</a>', re.S)  # 教育信息
    certif = re.compile(r'class="pf_intro" title="(.*?)">', re.S)  # 认证信息

    html = driver.page_source
    infos = re.findall(info, html)
    if (len(infos) == 0):
        driver.get('https://weibo.com/p/103505' + str(uid) + '/info?mod=pedit_more')  # 大V资料页
        time.sleep(2)
        html = driver.page_source
        infos = re.findall(info, html)

    jobs = re.findall(job, html)
    edus = re.findall(edu, html)
    cer = re.findall(certif, html)
    Uname = ''
    Certified = ''
    Sex = ''
    Relationship = ''
    Area = ''
    Birthday = ''
    Education_info = ''
    Work_info = ''
    Description = ''
    for Cert in cer:
        Certified += Cert

    for job in jobs:
        Work_info += job + ' '
    for edu in edus:
        Education_info += edu + ' '

    for inf in infos:
        tmpstr = re.findall(information, inf)
        con = re.findall(content, inf)
        if (len(tmpstr) == 0):
            continue
        if (len(con) == 0):
            con = ''
        else:
            con = con[0]
        tmpstr = tmpstr[0]
        if (tmpstr == '昵称'):
            Uname = con
        elif (tmpstr == '性别'):
            Sex = con
        elif (tmpstr == '感情状况'):
            Relationship = con
        elif (tmpstr == '所在地'):
            Area = con
        elif (tmpstr == '生日'):
            Birthday = con
        elif (tmpstr == '简介'):
            Description = con
    print('Uname=' + Uname, 'Certified=' + Certified, 'Sex=' + Sex, 'Relationship=' + Relationship,
          'Area=' + Area, 'Birthday=' + Birthday, 'Education_info=' + Education_info, 'Work_info=' + Work_info,
          'Description=' + Description)

    ins = insert(table).values(uid=uid, Uname=Uname, Certified=Certified, Sex=Sex, Relationship=Relationship, Area=Area,
                               Birthday=Birthday, Education_info=Education_info, Work_info=Work_info,
                               Description=Description)
    ins = ins.on_duplicate_key_update(
        # 如果不存在则插入，存在则更新(upsert操作http://docs.sqlalchemy.org/en/latest/dialects/mysql.html#mysql-insert-on-duplicate-key-update)
        Uname=Uname, Certified=Certified, Sex=Sex, Relationship=Relationship, Area=Area,
        Birthday=Birthday, Education_info=Education_info, Work_info=Work_info, Description=Description
    )
    conn.execute(ins)


def execute_times(driver):
    dynamic = []
    T = []
    d = re.compile(r'og"><div class="weibo-text">(.*?)<', re.S)  # 匹配动态
    t = re.compile(r'<span class="time">(.*?)<', re.S)  # 匹配动态发布时间

    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # 滑动到底
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # 等待加载
        time.sleep(random.random())

        # 计算新的滚动高度并与上一个滚动高度进行比较
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    html = driver.page_source

    dynamic += re.findall(d, html)
    T += re.findall(t, html)
    return dynamic, T


def getmain(cookies, uid, conn, table_data, table_user):
    opt = webdriver.ChromeOptions()  # 创建chrome参数对象
    opt.set_headless()  # 把chrome设置成无头模式，不论windows还是linux都可以，自动适配对应参数
    driver = webdriver.Chrome(options=opt)
    driver.get("http://weibo.com")
    time.sleep(3)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()

    getinfo(conn, driver, uid, table_user)#获取资料页
    time.sleep(2)
    driver.get("https://m.weibo.cn/p/100505" + str(uid) + "#feedtop")
    time.sleep(2)
    dynamics, times = execute_times(driver)
    time.sleep(2)
    driver.close()
    print('end------------------------------------------')
    '''
    正则表达式组
    '''
    re_nbsp = re.compile(r'&nbsp', re.S)  # 去除$nbsp
    re_html = re.compile(r'</?\w+[^>]*>', re.S)  # 去除html标签
    re_200b = re.compile(r'\u200b', re.S)  # 去除分隔符
    re_quot = re.compile(r'&quot', re.S)
    today_time = re.compile(r'\d+小时前', re.S)
    yesterday_time = re.compile(r'昨天', re.S)
    recent_time = re.compile(r'^\d{2}-\d{2}$', re.S)
    emoji_pattern = re.compile(#去除表情,有些超过了'utf8mb4'编码范围,暂时不把表情存入数据库
        u"(\ud83d[\ude00-\ude4f])|"  # emoticons
        u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
        u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
        u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
        u"(\ud83c[\udde0-\uddff])|"  # flags (iOS)
        u"[\U00010000-\U0010ffff]|[\uD800-\uDBFF][\uDC00-\uDFFF]"
        "+", re.S)

    strtoday = datetime.date.today()
    stryesterday = strtoday - datetime.timedelta(days=1)
    today = strtoday.strftime('%m月%d日')
    yesterday = stryesterday.strftime('%m月%d日')


    for i in range(len(times)):
        # 将时间中的今天(**小时前),昨天(昨天 **)和最近(month-day)这三特殊情况转化为'month月day日'格式
        istoday = re.findall(today_time, times[i])
        isyesterday = re.findall(yesterday_time, times[i])
        isrecenttime = re.findall(recent_time, times[i])

        if (istoday):  # 列表不为空
            times[i] = today + ' ' + str(i)
        elif (isyesterday):
            times[i] = yesterday + ' ' + str(i)
        elif (isrecenttime):
            times[i] += '日'
            times[i] = times[i].replace('-', '月') + ' ' + str(i)
        dynamics[i] = dynamics[i].strip()
        dynamics[i] = re_nbsp.sub('', dynamics[i])
        dynamics[i] = re_html.sub('', dynamics[i])
        dynamics[i] = re_200b.sub('', dynamics[i])
        dynamics[i] = re_quot.sub('', dynamics[i])
        dynamics[i] = emoji_pattern.sub('', dynamics[i])
        ins = insert(table_data).values(uid=uid, weibo_cont=pymysql.escape_string(dynamics[i]), create_time=times[i])
        ins = ins.on_duplicate_key_update(weibo_cont=pymysql.escape_string(dynamics[i]))
        conn.execute(ins)



def main():
    conf, engine = Connect('conf.yaml')  # 获取配置文件的内容
    uids = conf.get('uids')
    uids = list(uids.values())
    cookies = pickle.load(open('cookies.pkl', 'rb'))
    conn = engine.connect()
    metadata = MetaData(engine)
    wb_user = Table('wb_user', metadata, autoload=True)  # Table Reflection 个人信息表
    wb_data = Table('wb_data', metadata, autoload=True)  # 动态表
    for uid in uids:
        getmain(cookies, uid, conn, wb_data, wb_user)
    conn.close()


if __name__ == '__main__':
    main()
