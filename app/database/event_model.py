import db

class EventModel():

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
        if not isinstance(df, type(None)):
            return True
        else:
            return False
