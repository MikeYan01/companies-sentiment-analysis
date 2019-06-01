# coding=utf-8
from sklearn.externals import joblib
from sklearn.svm import SVC

class ChiSquare:
    def __init__(self, train_data, train_labels):
        self.all_dict, self.pos_dict, self.neg_dict = {}, {}, {} # (word, word's occurence)
        self.words_ChiSquare = {}

        for i, data in enumerate(train_data):
            for word in data:
                self.all_dict[word] = self.all_dict.get(word, 0) + 1
                if train_labels[i] == 1:
                    self.pos_dict[word] = self.pos_dict.get(word, 0) + 1

        total_pos_freq = sum(self.pos_dict.values())
        total_freq = sum(self.all_dict.values())
        for each_word, freq in self.all_dict.items():
            value = self.func(self.pos_dict.get(each_word, 0), freq, total_pos_freq, total_freq)
            self.words_ChiSquare[each_word] = value
    
    @staticmethod
    def func(word_pos_freq, word_freq, total_pos_freq, total_freq):
        n11 = word_pos_freq
        n10 = word_freq - word_pos_freq
        n01 = total_pos_freq - word_pos_freq
        n00 = total_freq - n11 - n01 - n10
        return total_freq * (float((n11*n00 - n01*n10)**2) / ((n11 + n01) * (n11 + n10) * (n01 + n00) * (n10 + n00)))

    # Sort all words by Chi-Square value, highest to lowest
    # The first k words will become features
    def get_features(self, k): 
        words = sorted(self.words_ChiSquare.items(), key=lambda d: d[1], reverse=True)
        return [word[0] for word in words[:k]]
        

class SVM:
    def __init__(self, features):
        self.features = features

    def words2vec(self, all_data):
        index = {} # (Feature word, Feature word's position)
        for i, word in enumerate(self.features):
            index[word] = i

        # Change of vectors
        all_vecs = []
        for data in all_data:
            vec = [0 for each in range(len(self.features))]
            for word in data:
                i = index.get(word)
                if i is not None:
                    vec[i] += 1
            all_vecs.append(vec)
        return all_vecs

    def train(self, train_data, train_labels, C):
        self.svc = SVC(C=C)
        train_vec = self.words2vec(train_data)
        self.svc.fit(train_vec, train_labels)
        joblib.dump(self.svc, "../model/train_model.pkl")

    def predict(self, test_data):
        # self.svc = joblib.load("../model/train_model.pkl")
        vec = self.words2vec([test_data])
        result = self.svc.predict(vec)
        return result[0]