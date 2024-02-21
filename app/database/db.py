import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

class DB():
    eg = None
    session = None 
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
            self.eg = create_engine(f"postgresql+psycopg2://{params['user']}:{params['password']}@{params['host']}:{params['port']}/{params['dbname']}", isolation_level='SERIALIZABLE')
            self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.eg))
        return True if ((self.eg != None) & (self.session != None)) else False

    def disconnect(self):
        if self.eg != None:
            self.eg.dispose()

    def execute(self, sql):
        return self.session().execute(sql)

    def select(self, sql):
        return pd.read_sql_query(sql, self.session().bind)