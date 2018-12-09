# 网络爬虫程序，主要完成从指定URL开始递归下载相关网页，并建立索引。

import argparse
import requests
from collections import deque 
import re
from bs4 import BeautifulSoup
import sqlite3
import jieba


class spider():
    def __init__(self, seed_url, target_url_count):
        self.seed_url = seed_url
        self.target_url_count = target_url_count
        self.cur_url_count = 0
        self.patten = re.compile(r'<a href=\"([0-9a-zA-Z\_\/\.\%\?\=\-\&\:]+)\"', re.I)
        self.__queue__ = deque()
        self.__visited__ = set()
        self.__queue__.append(self.seed_url)
        
    def get_next_url(self):
        if self.__queue__: 
            url = self.__queue__.popleft()
            self.__visited__.add(url)
            return  url
        else :
            return None

    def get_context(self, url):
        web = requests.get(url)
        return web.text

    def extract_text(self, context):
        soup = BeautifulSoup(context, 'lxml')

        if soup.title == None:
            return  None, None
        else:
            title = soup.title.string
            if (title == '404') or (title.find('403') != -1) or (title == None):
                return  None, None
         
        # 分析网页提取文本
        text_article="" 
        text_title = soup.title.string.strip()

        # 提取文字
        article = soup.find_all('article')

        len_article = len(article)
        if len_article < 1:
            text_article = 'None' # 空白文档
        else:
            for index in article :
                tag_p = index.find_all('p')
                for text in tag_p :
                    text_article += text.text.strip()
            text_article.replace(" ", "")
    
        return text_title, text_article


    def extract_url(self, context, purl):
        soup = BeautifulSoup(context, 'lxml')
        if soup.title :
            title = soup.title.string
            if (title == '404') or (title.find('403') != -1) or (title == None):
                return -1
            else:
                # 提取可用的url
                urls = self.patten.findall(context)
                for url in urls:
                    if not re.match(r'http', url):
                        url = purl+url
                    if (url not in self.__queue__) and (url not in self.__visited__) and (url[-1] != '/'):
                        self.__queue__.append(url)

                return len(urls)
        else:
            return -1
    

    def store_word(self, db, title, text, url):
        url_index = db.store_url(url, title)

        if text != 'None' :
            seggen = jieba.cut_for_search(title+text)
            seglist = list(seggen)
            for word in seglist:
                db.store_word(word, url_index)
            db.commit()


    def run(self, db):
        while self.cur_url_count < self.target_url_count:
            url = self.get_next_url()
            if url:
                context = self.get_context(url)
                self.extract_url(context, url)
                title, text = self.extract_text(context)
                if title:
                    self.store_word(db, title, text, url)
                    self.cur_url_count+=1
                    print(str(self.cur_url_count)+"\t"+url+"\t\t"+title)
            else:
                break


    def __test__(self):
        #if()
        pass


class db():
    def __init__(self, db_name):
        self.name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        try :
            print("删除旧的表文件")
            self.cursor.execute('drop table doc')
            self.cursor.execute('drop table word')
        except :
            print('数据库不存在，现在创建')

        print("创建新表")
        self.cursor.execute('create table doc (id integer primary key autoincrement, title text, link text)')
        self.cursor.execute('create table word (term varchar(25) primary key, list text)')

    def store_url(self, title, url):
        self.cursor.execute('insert into doc (title, link)values(?,?)', (title, url))
        cnt = self.cursor.execute('select count(1) from doc') # 获取当前数据库中有多少条数据
        self.conn.commit()
        return cnt.fetchall()[0][0]
 
    def store_word(self, word, url_index):
        self.cursor.execute('select list from word where term=?', (word,))
        result = self.cursor.fetchall()
        if len(result) == 0:
            docliststr = str(url_index)
            self.cursor.execute('insert into word values(?,?)', (word, docliststr))
        else:
            docliststr = result[0][0]
            docliststr +=' '+str(url_index)
            self.cursor.execute('update word set list=? where term=?', (docliststr, word))

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()







def main():
    parse =  argparse.ArgumentParser(description="递归下载指定URL的网页")
    parse.add_argument("url", type=str, help="seed url")
    parse.add_argument("words_database", type=str, help="database name to store words table")
    parse.add_argument('-c', '--count', type=int, default=1000, help='number of webs to index')
    args = parse.parse_args()


    target_url_cnt = args.count
    database = args.words_database
    seed_url = args.url

    word_db = db(database)
    word_db.create_tables()

    sp = spider(seed_url, target_url_cnt)

    sp.run(word_db)




if __name__ == '__main__':
    main()
