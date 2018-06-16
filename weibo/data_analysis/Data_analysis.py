"""
@author:ACool(www.github.com/starFalll)
根据微博用户动态进行词云和词频分析
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

#分词并去除停用词
def word_segmentation(content, stop_words):

    # 使用 jieba 分词对文本进行分词处理
    jieba.enable_parallel()
    seg_list = jieba.cut(content)

    seg_list = list(seg_list)

    # 去除停用词
    word_list = []
    for word in seg_list:
        if word not in stop_words:
            word_list.append(word)

    # 过滤遗漏词、空格
    user_dict = [' ', '哒']
    filter_space = lambda w: w not in user_dict
    word_list = list(filter(filter_space, word_list))

    return word_list

#将数据库中的微博动态转化为字符串
def getstr(uid=1845675654):
    _,engine = Connect('../conf.yaml')  # 连接数据库
    conn = engine.connect()
    metadata = MetaData(engine)
    WBData = Table('WBData', metadata, autoload=True)
    s = select([WBData]).where(WBData.c.uid==uid)
    res = conn.execute(s)
    conn.close()
    str = ''
    for row in res:
        str += row[2] + '\n'
    return str

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

    chart.render()

def main():
    str=getstr(1497642751)#将数据库中的微博动态转化为字符串,可以指定uid(conf.yaml里面的)
    with open('data/stop_words.txt') as f:
        stop_words = f.read().split('\n')
    str=format_content(str)
    word_list=word_segmentation(str,stop_words)#分词并去除停用词
    create_wordcloud(word_list) #画出词云
    counter = word_frequency(word_list, 10)# 返回前 top_N 个值，如果不指定则返回所有值
    print(counter)
    plot_chart(counter)#会生成词频图保存在render.html中


if __name__=='__main__':
    main()
