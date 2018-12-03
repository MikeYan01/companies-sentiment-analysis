#coding=utf-8
import psycopg2

# 连接数据库
conn = psycopg2.connect(database="Market", user="mkt_reader",
                        password="Mkt2016midas", host="awspostgres.midastouching.com", port="5432")
cur = conn.cursor()
cur.execute("SELECT cont_summary FROM media WHERE company_id = '000756';")

# 写入原始数据
row = cur.fetchone()
count = 0
f = open('../midas_data/raw_data.txt', 'w')

while row is not None:
    f.write(str(row[0]))
    count += 1
    print(count)

    if count == 5000:
        break

    row = cur.fetchone()
f.close()

# 对原始数据进行分词，用于之后的语料库选取
import jieba
import jieba.posseg
import jieba.analyse

file_name = '../midas_data/raw_data.txt'
file_object = open(file_name)
file_context = file_object.read()

seg_list = jieba.cut(file_context, cut_all=False)

f = open('../midas_data/seg_data.txt', 'w')
f.write(" ".join(seg_list))

file_object.close()
f.close()
conn.commit()
conn.close()