from database import db

class Config():

    db = None

    def __init__(self, db):
        self.db = db

    def get_config(self, config_name):
        df = self.db.select(f"select * from config where key='{config_name}'")
        if self.is_valid(df):
            return df[df['key'] == config_name]['value'].item()
        else:
            return ''

    def set_config(self, config_name, str_value):
        sql = f"update config set value='{str_value}' where key='{config_name}'"
        self.db.execute(sql)

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

