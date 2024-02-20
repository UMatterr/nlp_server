import db

class Config():

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

    def get_config(self, config_name):
        if not self.is_valid(self.df):
            self.update()
        if self.is_valid(self.df):
            values = self.df[df['key'] == config_name].values
            if len(values) < 1:
                return ''
            else:
                return values[0]
        else:
            return ''

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

