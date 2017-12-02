import os
import csv
import sqlite3

class CSVWriter(object):

    def __init__(self, name, path=None):
        if os.path.exists(path):
            self.csv_path = os.path.join(path, name)
        else:
            self.csv_path = os.path.join(os.getcwd(), name)
        self.csv_file = open(self.csv_path, 'w')
        # The following line may not work on Linux
        # Checking the platform and processing it dynamically
        self.writer = csv.writer(self.csv_file, delimiter=',', lineterminator='\n', quoting=csv.QUOTE_ALL)

    def set_row(self, *args):
        if args:
            self.writer.writerow(tuple(v for v in args))

    def write_row(self, *args):
        if args:
            self.writer.writerow(tuple(v for v in args))

    def __del__(self):
        self.csv_file.close()


class SQLiteDB(object):

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


class HTMLTable(object):

    def __init__(self):
        pass