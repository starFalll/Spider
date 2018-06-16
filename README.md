# Spider
新浪微博(Sina weibo)，百度搜索结果 爬虫



## 使用方法：

环境：python3

推荐使用虚拟环境：

```
cd weibo
chmod u+x env.sh
./env.sh
```

全局安装（不使用虚拟环境）：

 `pip3 install -r requirements.txt`



具体说明请见源码。



## 微博用户信息分析

可以爬取微博用户个人资料以及动态信息。

数据分析：

-  生成词云
-  统计词频
-  使用 LDA 构建了**微博主题模型**
-  更多功能...

*UI:*

*      生成良好的UI数据分析与展示界面
  ​
  *更多功能还在开发中，程序也在不断重构中....*
  *代码行数++*


## 代码结构



    ├── baidu_result
    │   └── baidu_result.py	#根据关键词爬取百度搜索结果
    ├── LICENSE
    ├── README.md
    └── weibo
        ├── conf.yaml			#配置文件
        ├── Connect_mysql.py	#连接数据库
        ├── Create_all.py		#创建MySQL表
        ├── data_analysis		
        │   ├── data			
        │   │   └── stop_words.txt	#中文停用词
        │   ├── Data_analysis.py	#根据微博用户动态进行词云和词频分析
        │   ├── HYQiHei-25J.ttf		#用于生成中文词云的字体
        │   └── LDA_Analysis.py		#使用LDA进行微博动态主题建模与分析
        ├── Delete_users.py			#删除不在conf.yaml配置文件中的微博用户及其动态
        ├── env.sh					#该脚本可以使程序运行在虚拟环境中
        ├── __init__.py
        ├── requirements.txt		#项目依赖文件
        └── sina_spider.py			#爬取微博用户资料和动态并保存在数据库中