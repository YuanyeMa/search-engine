
import math
import argparse
import sqlite3
import jieba
from bs4 import BeautifulSoup
import requests


def main():
    parse = argparse.ArgumentParser(description="执行搜索操作")
    parse.add_argument("key_word", type=str, help="key word for search")
    parse.add_argument("words_database", type=str, help="database name to store words table")

    args = parse.parse_args()

    conn = sqlite3.connect(args.words_database)
    c = conn.cursor()
    c.execute('select count(1) from doc')
    N = 1+c.fetchall()[0][0] # 文档总数

    target = args.key_word

    seggen = jieba.cut_for_search(target)

    score = {}

    for word in seggen:
        print('得到查询词:', word)

        # 计算score
        tf = {}
        c.execute('select list from word where term=?', (word,))
        result = c.fetchall()

        if len(result)>0 :
            doclist = result[0][0]
            doclist = doclist.split(' ')

            doclist = [int(x) for x in doclist]

            df = len(set(doclist))
            idf = math.log(N/df)
            print('idf : ', idf)

            for num in doclist:
                if num in tf:
                    tf[num] = tf[num+1]
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

    cnt = 0
    for num, docscore in sortedlist:
        cnt=cnt+1
        c.execute('select link from doc where id=?', (num,))
        url = c.fetchall()[0][0]
        print(url, '得分 ： ', docscore)

        try:
            response = requests.get(url)
        except:
            print('Oops ... request failed!')
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.title
        if title == None:
            print('No title')
        else :
            title = title.text
            print(title)

        if cnt>20:
            break

    if cnt == 0:
        print('无搜索结果')

if __name__ == "__main__":
    main()

