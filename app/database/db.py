import psycopg2
import pandas as pd
from sqlalchemy import create_engine, sessionmaker

class DB():
    eg = None
    def __init__(self):
        self.connect()

    def connect(self):
        if self.eg == None:
            params = {
                'host':'umatter-test-db.c5u6k6y487pd.ap-southeast-2.rds.amazonaws.com',
                'dbname':'umatter_test_db',
                'user':'umatter_admin',
                'password':'umatteradmin!#',
                'port':5432
            }
            self.eg = create_engine(f"postgresql+psycopg2://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['dbname']}")
        return True if self.eg != None else False

    def disconnect(self):
        if self.eg != None:
            self.eg.dispose()

    def execute(self, sql):
        if self.eg != None:
            self.eg.execute(sql)
            

    def select(self, sql):
        if self.eg != None:
            df = pd.read_sql(sql, self.eg)
            print(df)
            return df 
        return None

    def update(self, sql):
        pass

    def delete(self, sql):
        pass
