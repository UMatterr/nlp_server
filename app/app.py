from flask import Flask, abort, request
from flask_restx import Api, Resource, reqparse
from transformers import GPT2LMHeadModel, AutoTokenizer
from os import path
import pandas as pd
import torch
import argparse
import utils
import time

from utils import g_q
from utils import g_w

from generator import chuseok
from database import db
from database import events
from database import input_texts

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError

g_sched = None
g_dbconn = None

app = Flask(__name__)
api = Api(app, title='NLP Server API', description=\
    'default 클릭해주세요\n\
    펼쳐지는 API 목록 중 events -> phrase -> converted 순으로 테스트 해주세요\n\
    -----------------------------------------------------------------\n\
    ---- "API 목록 -> Try it out" 클릭후 입력할 parameter ----\n\
    -----------------------------------------------------------------\n\
    status -> enabled or all 입력\n\
    event_id -> events 테스트 결과로 나온 숫자중 택 1\n\
    how -> formal or informal 입력\n\
    -----------------------------------------------------------------\n')

def none_or_empty(str):
    return (str == None) | (str == '')
        
def get_converted(src_list, convert_type, use_corrector):
    """문장 목록을 전달받아 존댓말,반말,그대로 등으로 변환하여 반환한다.

    Args:
        src_list (list of string): array of string
        convert_type (string): <formal|informal|asis>
        use_corrector (bool): <True|False>

    Returns:
        list of string: 변환된 문장 list
    """
    
    converted_list = None
    if convert_type == 'formal':
        converted_list = utils.toformal(src_list)
    elif convert_type == 'informal':
        converted_list = utils.toinformal(src_list)
    else:
        converted_list = src_list

    if use_corrector == True:
        return utils.correct(converted_list)
    else:
        return converted_list

# URL arguments 파서 정의
parser = reqparse.RequestParser()
# /phrase/<event_id>?use_cache=[1|0]&how=[informal|formal|asis]
parser.add_argument("use_cache", type=int)
parser.add_argument("how", type=str)
"""
# event id 가 기타에 해당하는 경우엔 keyword가 반드시 필요
# /phrase/99?use_cache=[1|0]&keyword=소개팅&src=<저장할 문장>
parser.add_argument("keyword", type=str)
# 사용자 위치에 따른 날씨 반영 (일단 seoul로 고정)
parser.add_argument("location", type=str)
# 위치와 연동할 정보 지정 (일단 날씨로 고정)
parser.add_argument("extrainfo", type=str)
# /converted/<how>?user_id=<보내는사람id>&friend_id=<받는사람id>&src=<변환할 문장>
parser.add_argument("user_id", type=str)
parser.add_argument("friend_id", type=str)
parser.add_argument("src", type=str)
"""

@api.route('/events/<string:status>')
class Events(Resource):
    
    def get(self, status):
        """ 이벤트 목록을 반환한다 status: <all, enabled, disabled> -> 현재는 all로만 동작
        Examples 1: GET /events/all
        Examples 2: GET /events/enabled
        Exmaples 3: GET /events/disabled

        Returns: {'events':[{'event_id':'event_name'}...]}
        """
        assert(g_dbconn)
        s = g_dbconn.session()

        try:
            tb_events = events.Events(g_dbconn)
            event_list = tb_events.get_list()
        except Exception as e:
            s.flush()
            s.rollback()
            print("An excetion occured on GET /events")
            print(e)
        else:
            s.commit()
        finally:
            s.close()

        return_events = []
        for item in event_list:
            return_events.append({item[0]:item[1]})
        return {'events':return_events}

@api.route('/phrase/<string:event_id>')
class Phrase(Resource):
    
    def get(self, event_id):
        """이벤트 문구를 반환한다 event_id: 이벤트 종류 id
        Args: use_cache (Optional): cache 사용 여부 [1|0], default(0), how (Optional): 반말/존댓말/그대로 [informal|formal|asis]

        Examples 1: GET /phrase/2?use_cache=0&how=informal     <- 새해(2), 새로 생성한 메시지(use_cache=0), 반말(how=informal)

        Returns: {'phrase':['문장1', '문장2', '문장3'}
        """
        use_cache = parser.parse_args()['use_cache']
        if use_cache == None:
            use_cache = 0

        how = parser.parse_args()['how']
        if how == None:
            how = 'asis'

        event_id = int(event_id)
        use_cache = bool(use_cache)

        assert(g_dbconn)
        s = g_dbconn.session()

        messages = []
        try:
            messages += (utils.get_five_messages(g_dbconn, event_id, use_cache, how))
        except Exception as e:
            s.flush()
            s.rollback()
            print("An excetion occured on GET /phrase")
            print(e)
        else:
            s.commit()
        finally:
            s.close()

        return {'phrase': messages}

    def post(self, event_id):
        """이벤트 문구를 저장한다 event_id: 이벤트 종류 id
        Args: 
        
        Examples 1: POST /phrase/1  -> 1:연말 인사
                    BODY: { "content": ["sentence to store1", "sentence to store2"] }
        
        Returns: {'result':'ok | error'}
        """
        ret = "error"
        event_id = int(event_id)
        content = request.json.get('content')
        
        assert(g_dbconn)
        s = g_dbconn.session()

        try:
            utils.add_user_inputs(g_dbconn, event_id, content)
            #tb_input_texts = input_texts.InputTexts(g_dbconn)
            #tb_input_texts.add(event_id, content)
        except Exception as e:
            s.flush()
            s.rollback()
            print("An excetion occured on POST /phrase")
            print(e)
        else:
            s.commit()
            ret = "ok"
        finally:
            s.close()

        return {'result':ret}

@api.route('/converted/<string:how>')
class Converted(Resource):

    def post(self, how):
        """이벤트 문구를 (존댓말/반말)로 변환한다 

        Examples 1: POST /converted/formal  <- 존댓말 변환
        Examples 2: POST /converted/informal <- 반말 변환
                    BODY: { "content": ["sentence to convert1", "sentence to convert2"] }

        Returns: {'converted':['converted sentence1', 'converted sentence2'] }
        """
        content = request.json.get('content')

        return { "converted": get_converted(content, how, False)}

        
if __name__ == "__main__":

    # DB 연결
    if g_dbconn == None:
        g_dbconn = db.DB()
    assert(g_dbconn != None)
    s = g_dbconn.session()

    # 스케쥴러 
    if g_sched == None:
        g_sched = BackgroundScheduler(timezone='Asia/Seoul')
        g_sched.start()
        # 03시에 (pre_generate_num/10) 만큼 문장 생성하여 DB에 추가
        g_sched.add_job(utils.reflenish_cache_texts, 'cron', hour='5', minute='00', id='reflenish', args=[g_dbconn, -1, False, True])
        g_sched.add_job(utils.retrain, 'cron', hour='0', minute='00', id='retrain', args=[g_dbconn])

    try:
        utils.initialize_cache_texts(g_dbconn)
    except Exception as e:
        s.flush()
        s.rollback()
        print("An excetion occured on initialize_cache_texts")
        print(e)
    else:
        s.commit()
    finally:
        s.close()
    
    app.run(debug=False, host='0.0.0.0', port=8000)

    if g_dbconn != None:
        g_dbconn.disconnect()
        g_dbconn = None

    if g_sched != None:
        g_sched.shutdown()

    if g_w != None:
        g_w.join()

    if g_q != None:
        g_q.join()