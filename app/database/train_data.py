from database import db
from sqlalchemy import MetaData, Table, Column, Integer, BINARY, TIMESTAMP, select

class TrainData():
    """train_data 테이블을 다루기 위한 클래스
    """

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
        """훈련 데이터를 저장하고 train_reservation 테이블에 저장할 primary key를 반환한다. (1:1)

        Args:
            utf8_text (binary): bytea 타잎으로 저장할 훈련 데이터

        Returns:
            int4: primary key
        """
        ins = self.train_data.insert().values(data=utf8_text)
        r = self.db.execute(ins)
        return r.inserted_primary_key

    def get_train_data(self, id):
        """특정 id에 해당하는 훈련데이터를 문자열로 반환한다.

        Args:
            id (int4): primary key

        Returns:
            string: 훈련데이터
        """
        sel = select(self.train_data).where(self.train_data.c_id==id)
        for r in self.db.execute(sel):
            return r.data.decode('utf-8')
        else:
            return ''

    def is_valid(self, df):
        if not isinstance(df, type(None)) and (len(df) > 0):
            return True
        else:
            return False

