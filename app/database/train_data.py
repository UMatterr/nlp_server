from database import db
from sqlalchemy import MetaData, Table, Column, Integer, BINARY, TIMESTAMP, select


class TrainData():

    #df = None
    db = None
    train_data = None

    def __init__(self, db):
        self.db = db
        meta = MetaData()
        self.train_data = Table(
            'train_data', meta,
            Column('id', Integer, primary_key=True),
            Column('data', BINARY),
            Column('last_modified', TIMESTAMP),
        )

    def add_train_data(self, utf8_text):
        ins = self.train_data.insert().values(data=utf8_text)
        r = self.db.execute(ins)
        return r.inserted_primary_key

    def get_train_data(self, id):
        sel = select(self.train_data).where(self.train_data.c_id==id)
        for r in self.db.execute(sel):
            return r.data.decode('utf-8')
        else:
            return ''

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

