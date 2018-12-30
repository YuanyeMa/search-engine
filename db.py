import sqlite3

class DB():
    def __init__(self, db_name):
        self.name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def len(self):
        self.cursor.execute('select count(1) from doc')
        self.count = 1+self.cursor.fetchall()[0][0] # 文档总数
        return self.count

    def get_word_list(self, word):
        self.cursor.execute('select list from word where term=?', (word,))
        return self.cursor.fetchall()

    def get_url_title(self, url_id):
        self.cursor.execute('select link,title from doc where id=?', (url_id,))
        return self.cursor.fetchall()

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
