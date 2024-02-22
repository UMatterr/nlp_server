from database import db

class Models():
    """models 테이블을 다루기 위한 클래스
    """

    db = None

    def __init__(self, db):
        self.db = db

    def get_models_by_eventid(self, event_id, model_type):
        # event_id, type 이 일치하는 모델중 최신 버전을 가져온다.
        df = self.db.select(f"select M.* from models M inner join event_model EM on M.id = EM.model_id where EM.event_id = '{event_id}' and M.type = '{model_type}' order by M.version desc limit 1")
        if self.is_valid(df):
            l =  df[['path','base','token_path', 'token_base', 'train_prefix', 'min_length', 'max_length', 'top_p', 'top_k', 'repetition_penalty', 'no_repeat_ngram_size', 'temperature', 'use_cache', 'do_sample']].values[0].tolist()
            return l[0], l[1], l[2], l[3], l[4], l[5:]
        else:
            return '','','','','', [None, None, None, None, None, None, None, None, None]

    def is_valid(self, df):
        if not isinstance(df, type(None)) and (len(df) > 0):
            return True
        else:
            return False

