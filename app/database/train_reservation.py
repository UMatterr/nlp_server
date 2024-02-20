from database import db
from database import config
import pandas as pd

class TrainReservation():

    #df = None
    db = None

    def __init__(self, db):
        self.db = db
        self.update()

    def register(self, event_id, train_data_id):

        # event_id 에 해당하는 훈련용 model 중 event_model에 등록된 id를 구한다.
        event_model_id = self.get_event_model_id(event_id)
        if event_model_id < 0:
            return
        
        available_time = self.get_available_time() 

        sql = f"insert into train_reservation (start_time, enable, status, event_model_id, train_data_id) values ('{available_time}', true, 'N', {event_model_id}, {train_data_id})"
        self.db.execute(sql)
        

    def get_count(self, event_id):
        # 이미 동일한 event 에 대해 C(omplete) 그리고 E(rror) 가 아닌 상태로 train_reservation 에 등록된 경우가 있는지 확인한다.
        df = self.db.select(f"select count(*) from train_reservation TR inner join event_model EM on (EM.event_id = {event_id}) inner join models M on (M.id = EM.model_id and M.type = 'T') where (TR.status != 'C' and TR.status != 'E')")
        if self.is_valid(df):
            return df['count'].item()
        else:
            return 0

    def get_event_model_id(self, event_id):
        df = self.db.select(f"select EM.id from event_model EM inner join models M on(M.id = EM.model_id and M.type = 'T') where (EM.event_id = {event_id})")
        if self.is_valid(df):
            return df['id'].item()
        else:
            return -1
         
    def get_training_model(self):
        ### train_reservation 에 등록된 항목중 enable=True, status=N, start_time >= now()인 항목의 train_reservation.event_model_id로 event_model을 조회하여 model_id를 가져온다.
        ### model_id 로 models 를 조회하여 base 모델을 준비한다.
        now = pd.Timestamp.now()
        sql = f"select TR.train_data_id, M.path, M.base, M.token_path, M.token_base, M.train_prefix from train_reservation TR inner join event_model EM on (EM.id = TR.event_model_id) inner join models M on (M.id = EM.model_id and M.type='T') \
            where TR.enable=true and TR.status='N', TR.start_time < {now}"

        df = self.db.select(sql)
        if len(df) > 0:
            return df[['train_data_id', 'path', 'base', 'token_path', 'token_base', 'train_prefix']].values
        else:
            return []

    def update_train_status(self, train_data_id, status):
        # train_reservation - train_data 는 1:1관계이므로 train_data_id로 train_reservation 를 조회할 수 있다.
        sql = f"update train_reservation set status='{status}' where train_data_id={train_data_id}"
        self.db.execute(sql)


    def get_avaliable_time(self):

        tb_config = config.Config(self.db)
        
        min_retrain_start_hour = int(tb_config.get_config("min_retrain_start_hour"))
        max_retrain_end_hour = int(tb_config.get_config("max_retrain_end_hour"))
         
        df = self.db.select("select start_time from train_reservation order by start_time desc limit 1")
        if len(df) > min_retrain_start_hour:
            ts = df['start_time'].item()
            if ts.hour < max_retrain_end_hour:
                ts = ts + pd.offsets.Hour(1)
            else:
                ts = ts + pd.offsets.Hour(24 - max_retrain_end_hour)
        else:
            ts = pd.Timestamp.now()
            ts = ts + pd.offsets.Hour(24)
            if ts.hour > max_retrain_end_hour:
                ts = ts.replace(hour = 0)
            ts = ts.replace(minute = 0)
            ts = ts.replace(second = 0)
            ts = ts.replace(microsecond = 0)
            
        return ts

    def is_valid(self, df):
        if not isinstance(df, type(None)):
            return True
        else:
            return False

