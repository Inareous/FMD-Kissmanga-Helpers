import sqlite3

class DB:
    def __init__(self, file):
        self.create_connection(file)

    def create_connection(self, db_file):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)
    
    def execute_query(self, query):
        try:
            c = self.conn.cursor()
            c.execute(query)
        except sqlite3.Error as e:
            print(e)

    def create_table_kissmanga(self):
        sql_create_table = """CREATE TABLE IF NOT EXISTS masterlist (
                                    link TEXT PRIMARY KEY,
                                    title TEXT NOT NULL,
                                    authors TEXT,
                                    artists TEXT,
                                    genres TEXT,
                                    status TEXT,
                                    summary TEXT,
                                    numchapter INTEGER,
                                    jdn INTEGER
                                );"""
        self.execute_query(sql_create_table)
    
    def post_row(self, tablename, rec):
        try:
            c = self.conn.cursor()
            keys = ','.join(rec.keys())
            question_marks = ','.join(list('?'*len(rec)))
            values = tuple(rec.values())
            c.execute('INSERT OR REPLACE INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)
        except Exception as e:
            print("Error : Exception in inserting data ({})".format(e))

    def insert_data_bulk(self, tablename, entries):
        for _, entry in enumerate(entries):
                self.post_row(tablename, entry)

    def save_and_close(self):
        try:
            self.conn.commit()
            self.conn.close()
        except sqlite3.Error as e:
            print(e)