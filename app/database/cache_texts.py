from database import db

class CacheTexts():
    """cache_texts 테이블을 handling하기 위한 클래스
    """

    db = None

    def __init__(self, db):
        self.db = db

    def replenish(self, event_id, sentences):
        # 특정 event에 해당하는 문장을 cache_texts 테이블에 추가한다.
        if len(sentences) <= 0:
            return

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
        # 특정 event에 해당하는 문장중 enable 한 문장의 갯수를 구한다.
        df = self.db.select(f"select count(*) from cache_texts where event_id={event_id} and enable=true")
        if self.is_valid(df):
            return df['count'].item()
        else:
            return 0

    def get_random5(self, event_id):
        # 특정 event에 해당하는 :5개의 문장을 랜덤하게 추출하여 list 형태로 반환한다.
        df = self.db.select(f"select * from cache_texts where event_id={event_id} and enable=true order by random() limit 5")
        if self.is_valid(df):
            return df['cache_text'].to_list()
        else:
            return []

    def get_recent_samples(self, event_id, sample_cnt):
        # 특정 event에 해당하는 :5개의 문장을 랜덤하게 추출하여 list 형태로 반환한다.
        df = self.db.select(f"select * from cache_texts where event_id={event_id} order by id desc limit {sample_cnt}")
        if self.is_valid(df):
            return df['cache_text'].to_list()
        else:
            return []


    def is_valid(self, df):
        if not isinstance(df, type(None)) and (len(df) > 0):
            return True
        else:
            return False

