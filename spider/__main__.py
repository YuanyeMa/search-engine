from .spider  import Spider as spider
import argparse
from database.db import DB as db

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
