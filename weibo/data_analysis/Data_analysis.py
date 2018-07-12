"""
@author:ACool(www.github.com/starFalll)
根据微博用户动态进行词云,词频分析,和时间分析
"""
import jieba
from wordcloud import WordCloud
from sqlalchemy import create_engine, MetaData,Table, Column, Integer, String, ForeignKey,update,select
import re
from collections import Counter
from pyecharts import Bar, Pie
from weibo.Connect_mysql import Connect



#去掉表情和一些不必要的符号
def format_content(content):
    content = content.replace(u'\xa0', u' ')
    content = re.sub(r'\[.*?\]','',content)
    content = content.replace('\n', ' ')
    return content

#画出词云
def create_wordcloud(content,image='weibo.jpg',max_words=5000,max_font_size=50):

    cut_text = " ".join(content)
    cloud = WordCloud(
        # 设置字体，不指定就会出现乱码
        font_path="HYQiHei-25J.ttf",
        # 允许最大词汇
        max_words=max_words,
        # 设置背景色
        # background_color='white',
        # 最大号字体
        max_font_size=max_font_size
    )
    word_cloud = cloud.generate(cut_text)
    word_cloud.to_file(image)

# 分词并去除停用词
def word_segmentation(content, stop_words):
    # 使用 jieba 分词对文本进行分词处理
    jieba.enable_parallel()
    seg_list = jieba.cut(content)

    seg_list = list(seg_list)

    # 去除停用词
    user_dict = [' ', '哒']
    filter_space = lambda w: w not in stop_words and w not in user_dict
    word_list = list(filter(filter_space, seg_list))

    return word_list

#将数据库中的微博动态转化为字符串
def get_time_str(uid):
    _,engine = Connect('../conf.yaml')  # 连接数据库
    conn = engine.connect()
    metadata = MetaData(engine)
    wb_data = Table('wb_data', metadata, autoload=True)
    s = select([wb_data]).where(wb_data.c.uid==uid)
    res = conn.execute(s)
    conn.close()
    str = ''
    time_lists = []
    for row in res:
        str += row[2] + '\n'
        time_lists.append(row[3])
    return time_lists,str

# 词频统计
# 返回前 top_N 个值，如果不指定则返回所有值
def word_frequency(word_list, *top_N):
    if top_N:
        counter = Counter(word_list).most_common(top_N[0])
    else:
        counter = Counter(word_list).most_common()

    return counter

#画出词频图
def plot_chart(counter, chart_type='Bar'):
    items = [item[0] for item in counter]
    values = [item[1] for item in counter]

    if chart_type == 'Bar':
        chart = Bar('微博动态词频统计')
        chart.add('词频', items, values, is_more_utils=True)
    else:
        chart = Pie('微博动态词频统计')
        chart.add('词频', items, values, is_label_show=True, is_more_utils=True)

    chart.render('weibo_wordfrq.html')

#画出微博发布时间的统计图
def plot_create_time(time_lists):
    recent_time = re.compile(r'\d{2}月\d{2}日',re.S)
    long_time = re.compile(r'(\d{4}-\d{2}-\d{2})',re.S)
    tmp_lists = []#保存**月**日格式的数据
    tmp_nums = []#统计**月**日发帖数量
    long_lists = []#保存20**-**-**格式的数据
    long_nums = []#统计20**-**-**发帖数量
    for t in time_lists:
        res = re.findall(recent_time, t)
        if(res):#res[0]为**月**日格式的数据

            if(not tmp_lists or res[0]!= tmp_lists[-1]):#列表为空或者不与前一个日期重复
                tmp_lists.append(res[0])
                tmp_nums.append(1)
            else:#与前一个日期重复，计数加一
                tmp_nums[-1]+=1
        else:#res[0]20**-**-**格式的数据
            res = re.findall(long_time,t)

            if(not long_lists or res[0]!=long_lists[-1]):
                long_lists.append(res[0])
                long_nums.append(1)
            else:
                long_nums[-1]+=1
    #将时间按照从远到进的顺序排列
    tmp_lists.reverse()
    tmp_nums.reverse()
    long_lists.reverse()
    long_nums.reverse()
    time_list = long_lists + tmp_lists
    time_nums = long_nums + tmp_nums
    chart = Bar('用户微博动态发布时间')
    chart.add('动态数', time_list, time_nums, is_more_utils=True,datazoom_range=[10,40],is_datazoom_show=True)
    chart.render("weibo_dynamic.html")

#可以指定需要分析的用户的uid（必须先存在conf.yaml里面，并且运行了一次sina_spider程序）
def main(uid):
    time_lists,str=get_time_str(uid)#将数据库中的微博动态转化为字符串
    plot_create_time(time_lists)
    with open('data/stop_words.txt') as f:
        stop_words = f.read().split('\n')
    str=format_content(str)
    word_list=word_segmentation(str,stop_words)#分词并去除停用词
    create_wordcloud(word_list) #画出词云
    counter = word_frequency(word_list, 10)# 返回前 top_N 个值，如果不指定则返回所有值
    print(counter)
    plot_chart(counter)#会生成词频图保存在weibo_wordfrq.html中


if __name__=='__main__':
    conf, _ = Connect('../conf.yaml')
    uid = conf.get('uids')
    uid = list(uid.values())[0]
    main(uid)#指定需要分析的用户的uid（必须先存在conf.yaml里面，并且运行了一次sina_spider程序），默认为conf.yaml中的第一条uid
