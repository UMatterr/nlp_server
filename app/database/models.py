import db

class Models():

    db = None

    def __init__(self, db):
        self.db = db
        self.update()

    def update(self):
        pass
        if self.db != None:
            self.df = self.db.select("select * from models where type='S'")
        else:
            self.df = None

    def get_models_by_eventid(self, event_id, model_type):
        # event_id, type 이 일치하는 모델중 최신 버전을 가져온다.
        df = self.db.select(f"select M.* from models M inner join event_model EM on M.id = EM.model_id where EM.event_id = '{event_id}' and M.type = '{model_type}' order by M.version desc limit 1")
        # 일단 path, base만 반환하자
        if self.is_valid(df):
            return df[['path','base','token_path', 'token_base', 'train_prefix']].values[0].tolist()
        else:
            return ['','','','','']

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

