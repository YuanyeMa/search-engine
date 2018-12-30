#-*- coding: UTF-8 -*-
import math
import argparse
import sqlite3
import jieba
from bs4 import BeautifulSoup
import requests
from db import DB


class Search():
    def __init__(self, db_name):
        self.db = DB(db_name) 
        self.N = self.db.len()

    def search(self, wordlist):
        sortedlist = self.get_score_list(wordlist)
        cnt = 0

        url_list = []

        for num, docscore in sortedlist:
            cnt=cnt+1
            url_list.append(self.db.get_url_title(num))

            if cnt>20:
                break

        if cnt == 0:
            return None

        return url_list


    def get_score_list(self, wordlist):
        score = {}
        for word in wordlist:
            # 计算score
            tf = {} # 词频
            result = self.db.get_word_list(word)

            if len(result)>0 :
                doclist = result[0][0]
                doclist = doclist.split(' ')
    
                doclist = [int(x) for x in doclist]

                print(len(doclist))

                df = len(set(doclist)) # 包含该词的文档数，去掉重复出现的文档

                idf = math.log(self.N/df) # 逆文档频率 inverse document frequency
                print('idf : ', idf)

                for num in doclist:  # num对应的是url的id ，此处统计的是同一个词在同一篇文章中出现的次数
                    if num in tf:
                        tf[num] = tf[num]+1
                    else :
                        tf[num] = 1

                # tf 统计结束，计算score
                for num in tf:
                    if num in score:
                        # 如果该num文档已经有分数了，则累加
                        score[num] = score[num] + tf[num]*idf
                    else:
                        score[num] = tf[num]*idf
    
        sortedlist = sorted(score.items(), key=lambda d:d[1], reverse=True) 
        # score.items() 以列表的形式返回可遍历的(key,value) reverse = True 按照降序排列
        return sortedlist




def main():
    parse = argparse.ArgumentParser(description="执行搜索操作")
    parse.add_argument("key_word", type=str, help="key word for search")
    parse.add_argument("words_database", type=str, help="database name to store words table")

    args = parse.parse_args()
    target = args.key_word

    seggen = jieba.cut_for_search(target)
    
    search = Search(args.words_database)
    url_list = search.search(seggen)

    for index in url_list:
        print(index)
        print('{0}\t{1}'.format(index[0][0], index[0][1]))

if __name__ == "__main__":
    main()

