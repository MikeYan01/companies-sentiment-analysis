# 文件目录结构   
corpus/ 存放各种文本数据   
---- pos_data.txt 正面评价语料库   
---- neg_data.txt 负面评价语料库   
---- pos_dict.txt 正面关键词词典   
---- neg_dict.txt 负面关键词词典     

midas_data/ 存放midas数据库中爬取的数据    
---- media.csv 临时存放媒体文章数据   
---- raw_data.txt 原始数据   
---- seg_data.txt 经过分词后的数据，之后人工从中选取正/负面评价语料   
 
model/ 存放SVM训练生成的模型   
---- train_model.pkl 训练模型   

src/ 源代码目录   
---- rawData.py 从远程数据库下载数据，并进行分词，用于构建训练模型   
---- svm.py 特征提取算法和SVM训练、预测   
---- dict.py 基于词典关键词的判断    
---- main.py 计算每篇文章的情感值    
---- midas_util.py 获取midas数据的相关工具函数   
---- media_cluster.py 对每家公司的舆情进行分时段分析，生成聚类结果    

README.md 本说明文件    
cluster.csv 聚类结果文件   

# 运行说明   
    · 运行main.py（命令行运行不需要输入参数），从midas数据库中获取原始文章进行分词和情感分析。替换原有的extend1标签     
    · 运行media_cluster.py（命令行运行需要输入server, 用户名, 密码等参数），对文章数据进行聚类，得到cluster.csv    

# 结果说明    
    · 每篇文章的预测结果由svm、词典两部分预测加权得到，目前设定的权值是svm 70%，词典 30%。根据最终值和0.5的大小关系，做出判断（<0.5为负，=0.5为中性，>0.5为正）   
    · 部分文章内容为空，统一设为中性    
    · cluster.csv中，num_cluster暂时设为10，对应10档公司健康度聚类结果    
