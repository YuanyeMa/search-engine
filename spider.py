# 网络爬虫程序，主要完成从指定URL开始递归下载相关网页，并建立索引。

import argparse
import requests
from collections import deque 
import re
from bs4 import BeautifulSoup
import sqlite3
import jieba

url_cnt=0
target_url_cnt=0

def analyze_web(queue, visited, content, purl, database):
    global url_cnt
    # 解析网页内容，并建立索引
    soup = BeautifulSoup(content, 'lxml')
    if soup.title :
        title = soup.title.string
        if (title == '404') or (title == '403') or (title == None):
            return 
        url_cnt += store_word(soup, purl, database)
    else :
        title = 'None'

    print(str(url_cnt)+"\t"+purl+"\t\t\t\t"+title.strip().replace(" ", ""))

    # 提取出页面内所有的链接，并加入队列
    pattern = re.compile(r'<a href=\"([0-9a-zA-Z\_\/\.\%\?\=\-\&\:]+)\"', re.I)
    urls = pattern.findall(content)
    
    for url in urls:
        if not re.match(r'http', url):
            url = purl+url
        if (url not in queue) and (url not in visited) and (url[-1] != '/'):
            queue.append(url)


def store_word(soup, url, database):
    text_article=soup.title.string.strip()

    # 提取文字
    article = soup.find_all('article')

    len_article = len(article)
    if len_article < 1:
        return 0 # 空白文档
    else:
        for index in article :
            tag_p = index.find_all('p')
            for text in tag_p :
                text_article += text.text.strip()
        #print(text_article)
    
    text_article.replace(" ", "")
    # 分词
    seggen = jieba.cut_for_search(text_article)
    seglist = list(seggen)

    # 存进数据库
    conn = sqlite3.connect(database)
    c = conn.cursor()

    c.execute('insert into doc (link)values(?)', (url,))

    cnt = c.execute('select count(1) from doc') # 获取当前数据库中有多少条数据
    cnt = cnt.fetchall()[0][0]

    for word in seglist:
        c.execute('select list from word where term=?', (word,))
        result = c.fetchall()
        if len(result) == 0:
            docliststr = str(cnt)
            c.execute('insert into word values(?,?)', (word, docliststr))
        else:
            docliststr = result[0][0]
            docliststr +=' '+str(cnt)
            c.execute('update word set list=? where term=?', (docliststr, word))

    conn.commit()
    conn.close()

    return 1

def create_database(databasename):
    conn = sqlite3.connect(databasename)
    c = conn.cursor()

    try :
        c.execute('drop table doc')
        c.execute('drop table word')
    except :
        print('数据库不存在，现在创建')
    c.execute('create table doc (id integer primary key autoincrement, link text)')
    c.execute('create table word (term varchar(25) primary key, list text)')

    conn.commit()
    conn.close()



def main():
    global url_cnt,  target_url_cnt

    parse =  argparse.ArgumentParser(description="递归下载指定URL的网页")
    parse.add_argument("url", type=str, help="seed url")
    parse.add_argument("words_database", type=str, help="database name to store words table")
    parse.add_argument('-c', '--count', type=int, default=1000, help='number of webs to index')

    args = parse.parse_args()
    
    target_url_cnt = args.count

    # 创建词表
    database = args.words_database
    create_database(database)
    
    # 爬取网页
    seed_url = args.url

    queue = deque() # 存储待搜索的url
    queue.append(seed_url)

    visited = set() # 存储已经访问过的url

    while queue :
        if url_cnt > target_url_cnt:
            break

        url = queue.popleft()
        visited.add(url)

        try:
            res = requests.get(url)
        except:
            print("open url failed!")
            continue
        
        analyze_web(queue, visited, res.text, url, database)

    print("共找到%s个url"% (url_cnt))
       



if __name__ == '__main__':
    main()
