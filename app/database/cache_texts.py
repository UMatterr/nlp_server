from database import db

class CacheTexts():

    #df = None
    db = None

    def __init__(self, db):
        self.db = db
        self.update()

    def replenish(self, event_id, sentences):
        # cache_texts 에 추가한다.
        table = "cache_texts"
        columns = [
            "cache_text", "enable", "event_id"
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
        df = self.db.select(f"select count(*) from cache_texts where event_id={event_id} and enable=true")
        if self.is_valid(df):
            return df['count'].item()
        else:
            return 0

    def get_random5(self, event_id):
        # 5개의 문장을 랜덤하게 추출하여 list 형태로 반환한다.
        df = self.db.select(f"select * from cache_texts where event_id={event_id} and enable=true order by random() limit 5")
        if self.is_valid(df):
            return df['cache_text'].to_list()
        else:
            return []

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

