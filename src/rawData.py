# coding=utf-8
import psycopg2

# For privacy, the detailed information about database is hidden
conn = psycopg2.connect(database="dbname", user="username",
                         password="password", host="hostname", port="portname")
cur = conn.cursor()
cur.execute("SELECT column_name FROM table_name WHERE conditions happen;")

# Write raw text to file
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

# Word segmentation
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