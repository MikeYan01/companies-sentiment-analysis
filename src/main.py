import pandas
from pandas import Series
import sys
import psycopg2
import pandas.io.sql as sqlio
import csv
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
import numpy as np
import time
import datetime
import re
import jieba
import jieba.posseg
import jieba.analyse
from svm import ChiSquare
from svm import SVM
from dict import Dict

def seg_article(article, seg_list):
    test_list = []

    # Word segmentation
    all = " ".join(seg_list)
    pattern = r'？|！|。|……'
    split = re.split(pattern, all)

    # Write to file, sentence by sentence
    for var in split:
        test_list.append(var.strip(' '))
    return test_list

def get_train_corpus(train_data):
    pos_path = "../corpus/pos_data.txt"
    neg_path = "../corpus/neg_data.txt"
    re_seg = re.compile("\s+")

    count = 0
    with open(pos_path, 'r') as p, open(neg_path, 'r') as n:
        for line in p:
            splits = re_seg.split(line.strip())
            train_data.append(splits[1:])
        count = len(train_data)
        for line in n:
            splits = re_seg.split(line.strip())
            train_data.append(splits[1:])
    train_labels = [1] * count + [0] * (len(train_data) - count)
    return train_labels

def test_article(article, svm, pos_dict, neg_dict):
    # Word segmentation on raw articles
    file_context = str(article)
    seg_list = jieba.cut(file_context.strip(), cut_all=False)
    test_data = seg_article(article, seg_list)

    # Pre-judge based on dictionary
    dict = Dict(file_context, seg_list)
    factor = dict.calculate_factor(test_data, pos_dict, neg_dict)

    # SVM's prediction
    result = []
    for each in test_data:
        if (each == '') is False:
            result.append(svm.predict(each))

    # Calculate points and normalize
    polar = np.mean(result)
    final_score = 0.7*polar + 0.3*factor
    if (final_score < 0.5):
        return '-1'
    elif (final_score == 0.5):
        return '0'
    else:
        return '1'

if __name__ == '__main__':
    print ('Program starts at: '+datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))

    # For privacy, the detailed information about database is hidden
    conn = psycopg2.connect(database="dbname", user="username", password="password", host="hostname", port="portname")
    qry = "query sql"
    
    df = sqlio.read_sql_query(qry, conn)
    print('Selection Finished. ' + datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))
    conn.commit()
    conn.close()

    #******************* Preprocessing ****************** 
    # Parameters' setting
    feature_num = 180
    C = 150

     # Positive and negative training corpus
    train_data = []
    train_labels = get_train_corpus(train_data)

    # Feature Extraction
    features = ChiSquare(train_data, train_labels).get_features(feature_num)
    svm = SVM(features)
    svm.train(train_data, train_labels, C)

    # Dictionaries
    pos_dict, neg_dict = [], []
    pos_dict_path = "../corpus/pos_dict.txt"
    neg_dict_path = "../corpus/neg_dict.txt"
    with open(pos_dict_path, 'r') as p, open(neg_dict_path, 'r') as n:
        for line in p:
            pos_dict.append(line.strip())
        for line in n:
            neg_dict.append(line.strip())

    #******************* Prediction *******************
    nlp_prediction = []
    for index, row in df.iterrows():
        each_article = row['cont_summary']
        if str(each_article) == 'None' or each_article == '':
            nlp_prediction.append('0')
        else:
            nlp_prediction.append( test_article(each_article, svm, pos_dict, neg_dict) )
    print('Prediction Finished. ' + datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))

    #******************* Result's replacement ********************
    del df['extend1']
    extend1 = Series(nlp_prediction)
    df['extend1'] = extend1
    print('Modification Finished. ' + datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))

    # Intermediate files for clustering
    df.to_csv('../midas_data/media.csv', columns = ['company_id', 'publish_time', 'extend1'])
    print ('Program ends at: ' + datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))