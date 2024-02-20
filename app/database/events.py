from database import db

class Events():

    df = None
    db = None

    def __init__(self, db):
        self.db = db
        self.update()

    def update(self):
        if self.db != None:
            self.df = self.db.select("select * from events")
        else:
            self.df = None

    def get_id_list(self):
        if not self.is_valid(self.df):
            self.update()
        if self.is_valid(self.df):
            return self.df['id'].to_list()
        else:
            return []


    def get_name_list(self):
        if not self.is_valid(self.df):
            self.update()
        if self.is_valid(self.df):
            return self.df['event_name'].to_list()
        else:
            return []

    def id2name(self, id):
        return self.df[self.df['id'] == id]['event_name'].item()

    def name2id(self, name):
        return self.df[self.df['event_name'] == name]['id'].item()

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

