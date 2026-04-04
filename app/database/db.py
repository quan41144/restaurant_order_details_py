import psycopg2
from app.config.db_config import DB_CONFIG

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()

    def execute(self, query, params=None):
        self.cur.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=None):
        self.cur.execute(query, params)
        return self.cur.fetchall()

    def fetch_one(self, query, params=None):
        self.cur.execute(query, params)
        return self.cur.fetchone()