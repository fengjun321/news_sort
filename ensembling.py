import os
import sys
from unicodedata import category

from unittest import result
import pymysql
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import hashlib

from xml.dom.minidom import Document
from pandas_datareader import test
from pyhanlp import *
from classification import sogou_corpus_path

IClassifier = JClass('com.hankcs.hanlp.classification.classifiers.IClassifier')
NaiveBayesClassifier = JClass('com.hankcs.hanlp.classification.classifiers.NaiveBayesClassifier')
LinearSVMClassifier = JClass('com.hankcs.hanlp.classification.classifiers.LinearSVMClassifier')
FileDataSet = JClass('com.hankcs.hanlp.classification.corpus.FileDataSet')
IDataSet = JClass('com.hankcs.hanlp.classification.corpus.IDataSet')
MemoryDataSet = JClass('com.hankcs.hanlp.classification.corpus.MemoryDataSet')
Evaluator = JClass('com.hankcs.hanlp.classification.statistics.evaluations.Evaluator')
FMeasure = JClass('com.hankcs.hanlp.classification.statistics.evaluations.FMeasure')
BigramTokenizer = JClass('com.hankcs.hanlp.classification.tokenizers.BigramTokenizer')
HanLPTokenizer = JClass('com.hankcs.hanlp.classification.tokenizers.HanLPTokenizer')
ITokenizer = JClass('com.hankcs.hanlp.classification.tokenizers.ITokenizer')
DOO = JClass('com.hankcs.hanlp.classification.corpus.Document')

sogou_corpus_path = os.path.dirname(os.path.abspath(__file__))+"/analyse/model/chinabao"

# process
for root, dirs, files in os.walk(sogou_corpus_path):
    dir_list = dirs
    file_list = files
    break

categorys = dir_list
arr_classifier = []
arr_index = []
arr_tokenizer = []
dict_acc = {}
def evaluate(index, classifier, tokenizer, test_x, test_y):
    model_path = sogou_corpus_path + "asscemble_" + classifier.getClass().getSimpleName() + str(index) + '.ser'
    if os.path.isfile(model_path):
        if index == 1 or index == 2:
            classifier = NaiveBayesClassifier(IOUtil.readObjectFrom(model_path))
        if index == 3 or index == 4:
            classifier = LinearSVMClassifier(IOUtil.readObjectFrom(model_path))
    else:
        training_corpus = FileDataSet().setTokenizer(tokenizer).load(sogou_corpus_path, "UTF-8", 0.9)
        classifier.train(training_corpus)

    right_cnt = 0 
    for i in range(len(test_x)):
        x = test_x[i]
        cate = classifier.classify(x)
        if cate == test_y[i]:
            right_cnt += 1
    
    arr_classifier.append(classifier)
    arr_index.append(index)
    arr_tokenizer.append(tokenizer)
    dict_acc[classifier.getClass().getSimpleName()+str(index)] = right_cnt / len(test_x)

    IOUtil.saveObjectTo(classifier.getModel(), model_path)
    return classifier.getClass().getSimpleName() + "+" + tokenizer.getClass().getSimpleName() + "精度:" + str(right_cnt / len(test_x))

def ensembling_evalue(test_x, test_y):
    a = sorted(dict_acc.items(), key=lambda x: x[1], reverse=False)
    b = [0.1] * len(arr_classifier)
    for i in range(len(a)):
        if i == 0:
            continue
        dec = a[i][1] - a[i-1][1]
        for j in range(i, len(a)):
            b[j] += dec 

    dict_power = {}
    for i in range(len(a)):
        item = a[i]
        dict_power[item[0]] = b[i]


    print(dict_power)
    acc_cnt = 0
    for i in range(len(test_x)):
        dict_category_score = {}
        for category in categorys:
            dict_category_score[category] = 0

        x = test_x[i]
        for j in range(len(arr_classifier)):
            classifer = arr_classifier[j]
            index = arr_index[j]
            cate = classifer.classify(x)
            dict_category_score[cate] += dict_power[classifer.getClass().getSimpleName()+str(index)]
        c = sorted(dict_category_score.items(), key=lambda x: x[1], reverse=True)
        
        if c[0][0] == test_y[i]:
            #print(c, test_y[i])
            acc_cnt += 1
        # else:
        #     print("err:", c, test_y[i])
    print("集成学习准确率:", acc_cnt / len(test_y))

connect = pymysql.connect(host='localhost',   # 本地数据库
                          user='root',
                          password='123456',
                          db='news_collect',
                          charset='utf8') #服务器名,账户,密码，数据库名称
cur = connect.cursor()



test_x = []
test_y = []
for category in categorys:
    cur.execute("select * from `%s` order by id desc limit 1000" % (category))
    result = cur.fetchall()
    result = list(result)

    for item in result:
        test_x.append(item[1])
        test_y.append(category)

msg_arr = []
msg_arr.append(evaluate(1, NaiveBayesClassifier(), HanLPTokenizer(), test_x, test_y))
msg_arr.append(evaluate(2, NaiveBayesClassifier(), BigramTokenizer(), test_x, test_y))
msg_arr.append(evaluate(3, LinearSVMClassifier(), HanLPTokenizer(), test_x, test_y))
msg_arr.append(evaluate(4, LinearSVMClassifier(), BigramTokenizer(), test_x, test_y))

for msg in msg_arr:
    print(msg)
ensembling_evalue(test_x, test_y)
