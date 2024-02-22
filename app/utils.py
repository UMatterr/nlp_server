import torch
from tqdm import tqdm
import queue
import threading

g_q = None
g_w = None

def generate(input_text, tokenizer, model, num):
    """훈련이 완료된 모델로 text를 생성하는 기능

    Args:
        input_text (string): text 생성을 위한 초기 문자열
        tokenizer (): transformer 모델 토커나이저
        model (): transformer 모델 
        num (int): 생성할 갯수

    Returns:
        list of string: 생성한 문자열을 list 타잎으로 반환
    """
    sentence_list = []
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    token_ids = tokenizer(input_text + "|", return_tensors="pt")["input_ids"].to(device)
    for cnt in tqdm(range(num)):
        gen_ids = model.generate(
            token_ids,
            max_length=32,
            repetition_penalty=2.0,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            bos_token_id=tokenizer.bos_token_id,
            use_cache=True,
            do_sample=True,
        )
        sentence = tokenizer.decode(gen_ids[0])
        sentence = sentence[sentence.index("|") + 1 :]
        if "<pad>" in sentence:
            sentence = sentence[: sentence.index("<pad>")].rstrip()
        sentence = sentence.replace("<unk>", " ").split("\n")[0]

        if cnt % 100 == 0 and cnt != 0:
            print(sentence)
        # sql 에 포함될때 오류를 방지하기 위해
        sentence = sentence.replace("'","")
        sentence_list.append(sentence)
    return sentence_list

def strings2trainable(train_prefix, string_list):
    #문자열 배열을 tagging된 훈련 데이터로 변환한다.
    train_data_list = []
    for s in string_list:
        if s.endswith('\n') == False:
            s += '\n'
        train_data_list.append(train_prefix + '|' + s)
    return ''.join(train_data_list).encode('utf-8')

##################################################################################################################
from generator import chuseok
from generator.common import CommonGenerator
from trainer.common import CommonTrainer
from converter import corrector
from converter import formal
from converter import informal
from database import db
from database import events
from database import models
from database import config
from database import cache_texts
from database import input_texts
from database import train_data
from database import train_reservation

g_service_generator = {}
g_typos_corrector = None
g_formal_converter = None
g_informal_converter = None

def correct(src_list):
    #문자열 list를 입력받아 맞춤법이 교정된 목록을 생성하여 반환한다.
    global g_typos_corrector
    if g_typos_corrector == None:
        g_typos_corrector = corrector.TyposCorrector()
    
    corrected_list = []
    for src in src_list:
        corrected_list.append(g_typos_corrector.convert(src))
    return corrected_list

def toformal(src_list):
    #문자열 list를 입력받아 존댓말로 변환된 목록을 생성하여 반환한다.
    global g_formal_converter
    if g_formal_converter == None:
        g_formal_converter = formal.ToFormalConverter()
    converted_list = []
    for src in src_list:
        converted_list.append(g_formal_converter.convert(src))
    return converted_list

def toinformal(src_list):
    #문자열 list를 입력받아 반말로 변환된 목록을 생성하여 반환한다.
    global g_informal_converter
    if g_informal_converter == None:
        g_informal_converter = informal.ToInformalConverter()
    converted_list = []
    for src in src_list:
        converted_list.append(g_informal_converter.convert(src))
    return converted_list

# <초기 cache 준비>
def initialize_cache_texts(dbconn):
    # 모든 event에 대해 문장을 생성하여 cache_texts에 채운다.
    assert(dbconn != None)

    tb_config = config.Config(dbconn)
    cache_texts_filled = tb_config.get_config('cache_texts_filled')

    if cache_texts_filled != '1':
        reflenish_cache_texts(dbconn, -1, True)
        tb_config.set_config('cache_texts_filled','1')


# <문장 준비>
# 각 event에 해당하는 문장을 생성하여 cache_texts 에 채운다.
# first가 True일때는 각 event별로 config.pre_generate_num 수만큼 생성 (최초)
# firsr가 False일때는 각 event별로 config.pre_generate_num/10 수만큼 생성 (cron 하루에 한번)
# event_id -1이 아닌 값이 주어지는 경우엔 해당 event만 처리한다.
def reflenish_cache_texts(dbconn, event_id, first=False, self_trasaction=False):

    global g_service_generator

    assert(dbconn != None)

    print(event_id)
    print(first)


    s = None
    if self_trasaction == True:
        s = dbconn.session()

    # first가 True 인 경우 각 이벤트 별로 pre_generate_num 수만큼 문장을 생성한다.
    # first가 False 인 경우 각 이벤트 별로 pre_generate_num/10 만큼 문장을 생성한다.
    tb_config = config.Config(dbconn)
    pre_generate_num = int(tb_config.get_config('pre_generate_num'))
    if first == True:
        generate_nums = pre_generate_num
    else:
        generate_nums = int(pre_generate_num/10)

    # 생성할 event 목록을 events 테이블에서 가져온다.
    event_ids = []
    if event_id == -1:
        tb_events = events.Events(dbconn)
        event_ids = tb_events.get_id_list()
    else:
        event_ids.append(event_id)
    
    tb_cache_texts = cache_texts.CacheTexts(dbconn)

    tb_models = models.Models(dbconn)
    # 각 event 에 해당하는 모델을 models 테이블에서 가져온다.
    # select M.* from models M inner join event_model EM on M.id = EM.model_id where EM.event_id = '1' and M.type='S' order by M.version desc limit 1
    for event_id in event_ids:
        path, base, token_path, token_base, train_prefix = tb_models.get_models_by_eventid(event_id, 'S')

        if event_id in g_service_generator:
            generator = g_service_generator[event_id]
        else:
            generator = CommonGenerator(path, token_path, train_prefix)
            g_service_generator[event_id] = generator

        # 각 모델별로 문장을 생성한다.
        # TODO: 맞춤범, 중복확인
        # 하나도 없을땐 최소 5개 생성한다.
        if generate_nums <= 0:
            generate_nums = 5

        if generate_nums > 0:
            sentences = generator.generateN(generate_nums)
            # cache_texts 테이블이 생성한 문장을 저장한다.
            if len(sentences) > 0:
                tb_cache_texts.replenish(event_id, sentences)

    if self_trasaction == True:
        s.commit()
        s.close()

        
# <문장 생성>
# 특정 이벤트에 해당하는 5개의 message를 구한다.
# use_cache 에 따라 cache_texts에 미리 생성된 문장을 사용하거나 실시간 생성한다.
## use_cache=1: cache_texts 에서 randon 하게 select, cache_texts에 5개가 없는 경우엔 use_cache=0인 경우와 동일하게 동작
## use_cache=0: event_model, models 에서 models.type=S 인 모델을 가져온다. -> 모델로 5개 생성하여 cache_texts에 insert 후 반환
# hot_to_convert 에 따라 존댓말, 반말 변환을 한다.
def get_five_messages(dbconn, event_id, use_cache, how_to_convert):

    assert(dbconn != None)

    tb_cache_texts = cache_texts.CacheTexts(dbconn)

    have_enough_cache = False
    if use_cache == True:
        # cache_texts 에 충분한 문장이 있는지 확인한다.
        available_cache_cnt = tb_cache_texts.get_count(event_id)
        if available_cache_cnt >= 5:
            have_enough_cache = True 

    if (have_enough_cache == False) or (use_cache == False):
        #  5개 생성 및 cache_text 에 삽입
        reflenish_cache_texts(dbconn, event_id)

        # 여기서 db에 반영해줘야 추출 가능
        dbconn.session().commit()
        dbconn.session().begin()

    # cache에서 5개 추출
    # TODO: 맞춤법은 생성할때 맞춘다.
    sentences = tb_cache_texts.get_random5(event_id)
    converted = None
    if how_to_convert == 'formal':
        converted = toformal(sentences)
    elif how_to_convert == 'informal':
        converted = toinformal(sentences)
    else:
        converted = sentences

    return converted 

def _ReservationWorker():
    global g_q

    while True:
        if g_q == None:
            break
        p_add_train_reservation, args = g_q.get()
        p_add_train_reservation(*args)

# <문장 수집>
# 특정 이벤트에 해당하는 사용자 입력을 재학습을 위해 input_texts 에 축적한다.
# 각 이벤트에 해당하는 message가 config.min_retrain_num 이상 쌓인 경우 재학습을 예약한다.
# 중복 허용 X
# queue 에서 받아서 별도의 thread 에서 돌리자 (db 연결도 별도)
def add_user_inputs(dbconn, event_id, input_text):

    assert(dbconn != None)

    global g_q
    global g_w

    if g_q == None:
        g_q = queue.Queue()
    if g_w == None:
        g_w = threading.Thread(target=_ReservationWorker)
        g_w.start()

    tb_config = config.Config(dbconn)
    min_retrain_num = int(tb_config.get_config("min_retrain_num"))

    have_enough_inputs = False
    tb_input_texts = input_texts.InputTexts(dbconn)
    tb_input_texts.add(event_id, input_text)

    available_input_texts_cnt = tb_input_texts.get_count(event_id)

    if available_input_texts_cnt >= min_retrain_num:
        have_enough_inputs = True

    if have_enough_inputs == True:
        g_q.put( (add_train_reservation, [dbconn, event_id, True]))



# <재학습 예약>
# 이미 동일한 이벤트에 대한 학습이 예약되어있는 경우 skip 한다.
# input_texts 에서 학습할 데이터를 추출하고 train 가능한 형태로 변환하여 train_data 에 저장하고 train_data.id를 구한다.
# train_data 에 저장한 data에 해당하는 항목을 input_texts 에서 disable 한다. 
# train_reservation 에 등록한다.
### event_model_id: event_model, models 에서 models.type=T(raining) 인 event_model.id 를 가져온다.
### train_data_id: train_data에 저장할때 반환된 id
### start_time: train_reservation 테이블을 조회하여 00~05시에 해당하는 시간에 훈련을 예약한다.
### enable: True
### status: N(ot started)
def add_train_reservation(dbconn, event_id, self_transaction):

    assert(dbconn != None)



    s = None
    if self_transaction == True:
        s = dbconn.session()

    try:

        tb_train_reservation = train_reservation.TrainReservation(dbconn)
        if tb_train_reservation.get_count(event_id) > 0:
            # 이미 동일한 이벤트에 대한 학습이 예약되어있는 경우 skip 한다.
            return

        # 1. input_texts 에서 학습할 데이터를 추출한다.
        # 2. train 가능한 형태로 변환한다. 
        # 3. train_data 에 저장하고 train_data.id를 구한다.
        # 4. train_data 에 저장한 data에 해당하는 항목을 input_texts 에서 disable 시킨다.
        tb_input_texts = input_texts.InputTexts(dbconn)
        input_ids, texts = tb_input_texts.get_input_texts(event_id)
        if len(input_ids) <= 0:
            # 학습할 데이터가 없다면 skip 한다.
            return

        tb_models = models.Models(dbconn)
        _, _, _, _, train_prefix = tb_models.get_models_by_eventid(event_id, 'T')
        data = strings2trainable(train_prefix, texts)

        tb_train_data = train_data.TrainData(dbconn)
        train_data_id = tb_train_data.add_train_data(data)

        tb_input_texts.disable_input_texts(input_ids)

        # train_reservation 에 등록한다.
        ### event_model_id: event_model, models 에서 models.type=T(raining) 인 event_model.id 를 가져온다.
        ### train_data_id: train_data에 저장할때 반환된 id
        ### start_time: train_reservation 테이블을 조회하여 00~05시까지 start_time이 가장 덜 겹치는 시간
        ### enable: True
        ### status: N(ot started)
        if len(train_data_id) > 0:
            train_data_id = train_data_id[0]
            tb_train_reservation.register(event_id, train_data_id)
    except Exception as e:
        print("An Exception occured in add_train_reservation")
        print(e)
        s.flush()
        s.rollback()
    else:
        s.commit()
    finally:
        if self_transaction == True:
            s.close()


# <재학습 기능>
# TODO: cron: min_retrain_start_hour 부터 max_retrain_end_hour 까지 1시간 간격으로 확인
# 모델준비
### train_reservation 에 등록된 항목중 enable=True, status=N, start_time >= now()인 항목의 train_reservation.event_model_id로 event_model을 조회하여 model_id를 가져온다.
### model_id 로 models 를 조회하여 base 모델을 준비한다.
# 데이터준비
### train_reservation.train_data_id 로 데이터를 가져온다.
# 재학습
### train_reservation.train_data_id 로 데이터를 가져온다.
### training 을 진행한다.
# 재학습 완료후 모델 저장
### model_id로 models를 조회하여 path를 가져온다.
### training 된 model을 huggingface 에 push 한다.
### train_reservation.status 를 C 또는 E로 바꾼다.
def retrain(dbconn):

    assert(dbconn != None)

    # 모델준비
    ### train_reservation 에 등록된 항목중 enable=True, status=N, start_time >= now()인 항목의 train_reservation.event_model_id로 event_model을 조회하여 model_id를 가져온다.
    ### model_id 로 models 를 조회하여 base 모델을 준비한다.
    ##### df[['train_data_id', 'path', 'base', 'token_path', 'token_base', 'train_prefix']].values
    tb_train_reservation = train_reservation.TrainReservation(dbconn)
    train_models = tb_train_reservation.get_training_model()

    tb_train_data = train_data.TrainData(dbconn)

    for models in train_models:
        # TODO: transaction 처리 고려
        # 데이터준비
        ### train_reservation.train_data_id 로 데이터를 가져온다.
        train_data_id = model[0]
        path = model[1]
        base = model[2]
        token_path = model[3]
        token_base = model[4]
        train_prefix = model[5]
        status = 'S'

        data = tb_train_data.get_train_data(train_data_id)

        # 재학습
        ### training 을 진행한다.
        trainer = CommonTrainer(base, token_base, train_prefix)

        tb_train_reservation.update_train_status(train_data_id, status)

        # TODO: 버전을 올린 T model을 models에 추가해야 할까??

        if trainer.train(data) == True:
            # 재학습 완료후 모델 저장
            ### model_id로 models를 조회하여 path를 가져온다. (get_train_data 에서 이미 가져옴)
            ### training 된 model을 huggingface 에 push 한다.
            ### train_reservation.status 를 C 또는 E로 바꾼다.
            trainer.push(path, token_path)
            status = 'C'
        else:
            status = 'E'

        tb_train_reservation.update_train_status(train_data_id, status)

