from database import db

def check_null(value):
    if value == None:
        value = "NULL"
    else:
        value = f"'{value}'"
    return value

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
            l =  df[['path','base','token_path', 'token_base', 'train_prefix', 'min_length', 'max_length', 'top_p', 'top_k', 'repetition_penalty', 'no_repeat_ngram_size', 'temperature', 'use_cache', 'do_sample', 'eos_token']].values[0].tolist()
            return l[0], l[1], l[2], l[3], l[4], l[5:]
        else:
            return '','','','','', [None, None, None, None, None, None, None, None, None, None]

    def add_model(self, name, type, path, base, version, desc, token_path, token_base, train_prefix, \
        min_length, max_length, top_p, top_k, repetition_penalty, no_repeat_ngram_size, temperature, use_cache, do_sample, eos_token):

        min_length = check_null(min_length)
        max_length = check_null(max_length)
        top_p = check_null(top_p)
        top_k = check_null(top_k)
        repetition_penalty = check_null(repetition_penalty)
        no_repeat_ngram_size = check_null(no_repeat_ngram_size)
        temperature = check_null(temperature)
        use_cache = check_null(use_cache)
        do_sample = check_null(do_sample)
        eos_token = check_null(eos_token)

        sql = f"insert into models (name, type, path, base, version, \"desc\", token_path, token_base, train_prefix, min_length, max_length, top_p, top_k, repetition_penalty, no_repeat_ngram_size, temperature, use_cache, do_sample, eos_token) values \
            ('{name}', '{type}', '{path}', '{base}', '{version}', '{desc}', '{token_path}', '{token_base}', '{train_prefix}', {min_length}, {max_length}, {top_p}, {top_k}, {repetition_penalty}, {no_repeat_ngram_size}, {temperature}, {use_cache}, {do_sample}, {eos_token})"
        self.db.execute(sql)


    def is_valid(self, df):
        if not isinstance(df, type(None)) and (len(df) > 0):
            return True
        else:
            return False

