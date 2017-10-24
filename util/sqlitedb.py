import os
import sqlite3


class SQLiteDB:

    def __init__(self, name, path=None):
        if os.path.exists(path):
            db = os.path.join(path, name)
        else:
            db = os.path.join(os.getcwd(), name)
        self.con = sqlite3.connect(db)
        self.con.text_factory = str()
        self.cursor = self.con.cursor()

    def query(self, q, *args):
        if not args:
            self.cursor.execute(q)
        else:
            self.cursor.execute(q, tuple(v for v in args))
        self.con.commit()

    def __del__(self):
        self.con.close()
