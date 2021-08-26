import psycopg2

class Database:

    def __init__(self):
        self.con = psycopg2.connect("dbname=sectest user=postgres host=localhost password=postgres")
        self.cur = self.con.cursor()

    def exec(self, query: str, params: tuple) -> tuple:
        self.cur.execute(query, params)
        try:
            result = self.cur.fetchall()
            self.con.commit()
            return result
        except:
            self.con.commit()
            return None  

    def close(self):
        self.cur.close()
        self.con.close()

