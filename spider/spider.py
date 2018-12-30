# 网络爬虫程序，主要完成从指定URL开始递归下载相关网页，并建立索引。

import argparse
import requests
from collections import deque 
import re
from bs4 import BeautifulSoup
from database.db  import DB as db
import jieba


class Spider():
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

