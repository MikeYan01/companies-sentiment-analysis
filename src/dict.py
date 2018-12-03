#coding=utf-8
import jieba
import jieba.posseg
import jieba.analyse
import math

class Dict:
    def __init__(self, article_context, seg_list):
        self.article_context = article_context
        self.seg_list = seg_list

    def calculate_factor(self, test_data, pos_dict, neg_dict):
        # 统计文章总词频，根据tf-idf算法选出代表性单词
        length = 0
        for each in self.seg_list:
            if len(each) > 1 and each != '\r\n':
                length += 1
        if length == 0:
            return 0.5
        tf_idf = jieba.analyse.extract_tags(self.article_context, math.ceil( length/50) )
    
        # 命中关键词，计算其对全文的综合影响力。tf_idf算法选出的代表词系数更高。
        pos_calc_dict, neg_calc_dict = {}, {}
        factor = 0.5
        for sentence in test_data:
            for word in sentence:
                if word in pos_dict:
                    if word not in pos_calc_dict:
                        pos_calc_dict[word] = 1
                    else:
                        pos_calc_dict[word] += 1
                elif word in neg_dict:
                    if word not in neg_calc_dict:
                        neg_calc_dict[word] = 1
                    else:
                        neg_calc_dict[word] += 1

        # 计算得分
        for key in pos_calc_dict:
            if key in tf_idf:
                factor += 60*pos_calc_dict[key]/length
            else:
                factor += 25*pos_calc_dict[key]/length

        for key in neg_calc_dict:
            if key in tf_idf:
                factor -= 60*neg_calc_dict[key]/length
            else:
                factor -= 25*neg_calc_dict[key]/length
        # 校正
        if factor > 1:
            factor = 1
        if factor < 0:
            factor = 0   
 
        return factor