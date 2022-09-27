import os
import sys

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

industrys = []
connect = pymysql.connect(host='localhost',   # 本地数据库
                          user='root',
                          password='123456',
                          db='mysql',
                          charset='utf8') #服务器名,账户,密码，数据库名称
admin = connect.cursor()
admin.execute("select * from `innodb_table_stats` where database_name = 'news_collect'")
tables = admin.fetchall()
for table in tables:
    industrys.append(table[1])
admin.close()
    
connect = pymysql.connect(host='localhost',   # 本地数据库
                          user='root',
                          password='123456',
                          db='news_collect',
                          charset='utf8') #服务器名,账户,密码，数据库名称
cur = connect.cursor()

print(industrys)

for industry in industrys:
    cur.execute("select * from `%s`" % (industry))
    result = cur.fetchall()
    result = list(result)
    result.sort(key=lambda x: x[4], reverse=False)
    print(result)

    l_date = []
    l_date_str = []
    for item in result:
        l_date.append(item[4])
    l_date = list(set(l_date))
    l_date.sort(reverse=False)
    

    l_cnt = []
    l_tmp = []
    for date in l_date:
        l_date_str.append(str(date))
        for x in result:
            print(x)
            if date >= x[4] and (date - x[4]).days <= 30:
                l_tmp.append(x)
        l_cnt.append(len(l_tmp))
        l_tmp = []

    base_dir = os.path.dirname(os.path.abspath(__file__))+"/analyse/model"
    china_bao = base_dir + "/chinabao"
    industry_dir = china_bao + "/" + industry
    if not os.path.exists(china_bao):
        os.mkdir(china_bao)

    if not os.path.exists(industry_dir):
        os.mkdir(industry_dir)

    idx = 0
    for x in result:
        f = open(industry_dir + "/" + str(idx) + ".txt", 'w',encoding='utf-8')
        print(industry, x)
        f.write(x[1] + "\n")
        f.write(x[2])
        idx += 1
        f.close()

    #保存图片
    print(l_date_str)
    print(l_cnt)
    fig = plt.figure()
    fig.suptitle(industry)
    plt.plot(l_date_str, l_cnt)
    plt.xticks(rotation=90)
    fig.savefig(os.path.dirname(os.path.abspath(__file__))+"/analyse/pic/" +industry+".jpg")
    #plt.show()

