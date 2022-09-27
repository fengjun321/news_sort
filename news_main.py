import pymysql
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import hashlib

connect = pymysql.connect(host='localhost',   # 本地数据库
                          user='root',
                          password='123456',
                          db='news_collect',
                          charset='utf8') #服务器名,账户,密码，数据库名称
cur = connect.cursor()

driver = webdriver.Chrome()

#加载栏目
industrys = []
try:
    driver.get('http://www.chinabgao.com/')

    element = WebDriverWait(driver,100).until(
            EC.presence_of_element_located((By.ID,"cateitems"))
        )

    cates = driver.find_elements(by=By.XPATH, value="//li[contains(@class, 'item')]/h3/a")
    for cate in cates:
        cate_href = cate.get_attribute("href")
        industrys.append(cate_href.split("/")[-2])
except:
    print("栏目加载失败")

#创建mysql数据库
for table in industrys:
    try:
        create_table = "CREATE TABLE `%s` ( \
            `id` bigint(20) NOT NULL AUTO_INCREMENT,\
            `title` varchar(255) DEFAULT NULL,\
            `content` varchar(255) DEFAULT NULL,\
            `hash` varchar(255) DEFAULT NULL,\
            PRIMARY KEY (`id`),\
            UNIQUE KEY `d` (`hash`) USING HASH,\
            `date1` date DEFAULT NULL, \
            `date2` timestamp NULL DEFAULT NULL\
            ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;" % (table)
        cur.execute(create_table)
    except:
        print("数据库table:%s已存在" % (table))
connect.commit()


def visit_detail():
    cur_url = driver.current_url
    views = driver.find_elements(by=By.XPATH, value="//div[contains(@class, 'listtitle')]/a")
    link_l = []
    for view in views:
        link_l.append(view.get_attribute("href"))

    ret = []
    for view_href in link_l:
        driver.get(view_href)
        try:
            element = WebDriverWait(driver,100).until(
                EC.presence_of_element_located((By.CLASS_NAME,"arctitle"))
            )

            pub_time = driver.find_element(by=By.XPATH, value="//span[contains(@class, 'pubTime')]")
            print(pub_time.text)
            arc_dec = driver.find_element(by=By.XPATH, value="//div[contains(@class, 'arcdec')]")
            print(arc_dec.text)

            ret.append((pub_time.text[:10], pub_time.text, arc_dec.text))
        except:
            ret.append(("", "", ""))

    driver.get(cur_url)
    element = WebDriverWait(driver,100).until(
        EC.presence_of_element_located((By.CLASS_NAME,"listcon"))
    )
    return ret

i = 0
print("当前插入栏目:", 'http://www.chinabgao.com/info/%s'%(industrys[i]))
driver.get('http://www.chinabgao.com/info/%s'%(industrys[i]))
try:
    while i < len(industrys):
        element = WebDriverWait(driver,100).until(
            EC.presence_of_element_located((By.CLASS_NAME,"listcon"))
        )

        list_title = []
        contents = driver.find_elements(by=By.CLASS_NAME, value='listtitle')
        for content in contents:
            list_title.append(content.text)
            #print(content.text)

        list_content = []
        contents = driver.find_elements(by=By.CLASS_NAME, value='preview')
        for content in contents:
            list_content.append(content.text)
            #print(content.text)

        next_href = ""
        try:
            next_link = driver.find_element(by=By.XPATH, value="//span[contains(@class, 'pagebox_next')]/a[text()='下一页']")
            next_href = next_link.get_attribute("href")
        except:
            pass

        detail = visit_detail()

        err_cnt = 0
        for j in range(len(list_title)):
            try:
                if detail[j][0] == "":
                    next_href = ""
                    break
                insert_sqli = "insert into `%s` (title, content, hash, date1, date2) values('%s', '%s', '%s', '%s', '%s');" % \
                    (industrys[i], list_title[j], detail[j][2], hashlib.md5(list_title[j].encode(encoding='UTF-8')).hexdigest(),
                    detail[j][0], detail[j][1])
                cur.execute(insert_sqli)
                connect.commit()
            except:
                #print("插入失败:", insert_sqli)
                err_cnt += 1
                pass

        #如果插入全部失败，则直接跳过
        if err_cnt == len(list_title):
            i += 1
            print("当前插入栏目:", 'http://www.chinabgao.com/info/%s'%(industrys[i]))
            driver.get('http://www.chinabgao.com/info/%s'%(industrys[i]))
            continue

        if next_href != "":
            driver.get(next_href)
        else:
            i += 1
            print("当前插入栏目:", 'http://www.chinabgao.com/info/%s'%(industrys[i]))
            driver.get('http://www.chinabgao.com/info/%s'%(industrys[i])) 
    
finally:
    driver.quit()

    #  ---------------------关闭数据库
    cur.close()  # 关闭游标
    connect.close()  # 关闭数据库连接

