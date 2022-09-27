# -*- coding:utf-8 -*-
# Author：hankcs
# Date: 2018-05-23 17:26
import os
import sys
from xml.dom.minidom import Document
sys.path.append('F:/test/nlp/pyhanlp')
print(sys.path)
from pyhanlp import SafeJClass
from test_utility import ensure_data

NaiveBayesClassifier = SafeJClass('com.hankcs.hanlp.classification.classifiers.NaiveBayesClassifier')
IOUtil = SafeJClass('com.hankcs.hanlp.corpus.io.IOUtil')
# sogou_corpus_path = ensure_data('搜狗文本分类语料库迷你版',
#                                 'http://file.hankcs.com/corpus/sogou-text-classification-corpus-mini.zip')

sogou_corpus_path = os.path.dirname(os.path.abspath(__file__))+"/analyse/model/chinabao"

def train_or_load_classifier():
    model_path = sogou_corpus_path + '.ser'
    print(model_path)
    if os.path.isfile(model_path):
        return NaiveBayesClassifier(IOUtil.readObjectFrom(model_path))
    classifier = NaiveBayesClassifier()
    classifier.train(sogou_corpus_path)
    model = classifier.getModel()
    IOUtil.saveObjectTo(model, model_path)
    return NaiveBayesClassifier(model)


def predict(classifier, text):
    print("《%16s》\t属于分类\t【%s】" % (text, classifier.classify(text)))
    # 如需获取离散型随机变量的分布，请使用predict接口
    # print("《%16s》\t属于分类\t【%s】" % (text, classifier.predict(text)))


if __name__ == '__main__':
    classifier = train_or_load_classifier()
    predict(classifier, "9月版号公布:73款游戏过审,腾讯网易收获今年首个版号 09-13 《巴比伦陨落》宣布将于2023年2月28日关服 曾达成单日最多在线人数 1 人成就 09-13 《九阴真经2》新三倍三份 金秋香气")
    print(classifier.classify("9月版号公布:73款游戏过审,腾讯网易收获今年首个版号 09-13 《巴比伦陨落》宣布将于2023年2月28日关服 曾达成单日最多在线人数 1 人成就 09-13 《九阴真经2》新三倍三份 金秋香气"))
