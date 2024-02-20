from database import db

class InputTexts():

    #df = None
    db = None

    def __init__(self, db):
        self.db = db

    def add(self, event_id, sentences):
        table = "input_texts"
        columns = [
            "input_text", "enable", "event_id"
        ]
        values = []
        for sentence in sentences:
            values.append(f"('{sentence}', true, {event_id})")
            
        s_columns = ', '.join(columns)
        s_values = ', '.join(values)
        query = f"INSERT INTO {table} ({s_columns}) VALUES {s_values}"
        self.db.execute(query)

    def get_count(self, event_id):
        # event_id 에 해당하는 문장중 enable 한 문장의 갯수를 구한다.
        df = self.db.select(f"select count(*) from input_texts where event_id={event_id} and enable=true")
        if self.is_valid(df):
            return df['count'].item()
        else:
            return 0

    def get_input_texts(self, event_id):
        # event_id 에 해당하는 문장중 enable 한 문장들을 list 형태로 반환한다.
        df = self.db.select(f"select * from input_texts where event_id={event_id} and enable=true")
        if self.is_valid(df) and (len(df) > 0):
            return df['id'].values, df['input_text'].values
        else:
            return [],[]

    def disable_input_texts(self, ids):
        for id in ids:
            sql = f"update input_texts set enable=false where id={id}"
            self.db.execute(sql)

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

