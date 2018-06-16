"""
@author:ACool(www.github.com/starFalll)
隐含狄利克雷分布（英语：Latent Dirichlet allocation，简称LDA）
一种主题模型，它可以将文档集中每篇文档的主题按照概率分布的形式给出。同时它是一种无监督学习算法，
在训练时不需要手工标注的训练集，需要的仅仅是文档集以及指定主题的数量k即可。此外LDA的另一个优点则是，
对于每一个主题均可找出一些词语来描述它。

本程序使用LDA进行微博动态主题建模与分析。

"""
from weibo.data_analysis.Data_analysis import getstr, format_content,word_segmentation
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from weibo.Connect_mysql import Connect
from sqlalchemy import create_engine, MetaData,Table, Column, Integer, String, ForeignKey,update,select
from sqlalchemy.dialects.mysql import insert

def getwords(uid=1497642751):
    str = getstr(uid)  # 将数据库中的微博动态转化为字符串,可以指定uid(conf.yaml里面的)
    with open('data/stop_words.txt') as f:
        stop_words = f.read().split('\n')
    str = format_content(str)
    word_list = word_segmentation(str, stop_words)  # 分词并去除停用词
    return word_list,uid

def Save_Topic_Words(model,feature_names, uid,n_top_words=20):
    _,engine=Connect('../conf.yaml')
    conn = engine.connect()
    metadata = MetaData(engine)
    WBTopic = Table('WBTopic', metadata, autoload=True)
    for topic_idx, topic in enumerate(model.components_):
        topics=topic_idx                                            #主题
        topic_conts=([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]])#主题
        for topic_cont in topic_conts:
            ins = insert(WBTopic).values(uid=uid,topic=topics,topic_cont=topic_cont)
            ins = ins.on_duplicate_key_update(
                topic=topics
            )
            conn.execute(ins)

    conn.close()

def word2vec(word_list,uid,n_features=1000,topics = 5):
    tf_vectorizer = CountVectorizer(strip_accents='unicode',
                                    max_features=n_features,
                                    #stop_words='english',
                                    max_df=0.5,
                                    min_df=10)
    tf = tf_vectorizer.fit_transform(word_list)

    lda = LatentDirichletAllocation(n_components=topics,#主题数
                                    learning_method='batch',#样本量不大只是用来学习的话用"batch"比较好，这样可以少很多参数要调
                                    )
    #用变分贝叶斯方法训练模型
    lda.fit(tf)

    #依次输出每个主题的关键词表
    tf_feature_names = tf_vectorizer.get_feature_names()
    Save_Topic_Words(lda,tf_feature_names,uid)

if __name__ == '__main__':
    wordlists,uid=getwords()
    word2vec(wordlists,uid)
