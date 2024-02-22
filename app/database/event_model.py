from database import db

class EventModel():
    """event_model 테이블을 핸들링하기 위한 클래스
    """

    df = None
    db = None

    def __init__(self, db):
        self.db = db
        self.update()

    def update(self):
        if self.db != None:
            self.df = self.db.select("select * from models where type='S'")
        else:
            self.df = None

    def is_valid(self, df):
        if not isinstance(df, type(None)) and (len(df) > 0):
            return True
        else:
            return False

