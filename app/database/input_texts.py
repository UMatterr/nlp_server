from database import db

class InputTexts():
    """input_texts 테이블을 핸들링하기 위한 클래스
    """

    db = None

    def __init__(self, db):
        self.db = db

    def add(self, event_id, sentences):
        # event_id 에 해당하는 문장들을 input_texts 에 저장한다.
        if len(sentences) <= 0:
            return

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
        if self.is_valid(df):
            return df['id'].values, df['input_text'].values
        else:
            return [],[]

    def disable_input_texts(self, ids):
        # 특정 id에 해당하는 input_texts를 diable 시킨다.
        for id in ids:
            sql = f"update input_texts set enable=false where id={id}"
            self.db.execute(sql)

    def is_valid(self, df):
        if not isinstance(df, type(None)) and (len(df) > 0):
            return True
        else:
            return False

