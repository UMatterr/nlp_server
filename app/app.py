from flask import Flask, abort, request
from flask_restx import Api, Resource, reqparse
from transformers import GPT2LMHeadModel, AutoTokenizer
import torch
import pandas as pd
import argparse
import utils
from os import path

from generator import chuseok

chuseok_generator = None

app = Flask(__name__)
api = Api(app, title='NLP Server API', description=\
    'default 클릭해주세요\n\
    펼쳐지는 API 목록 중 events -> phrase -> converted 순으로 테스트 해주세요\n\
    -> (convert 테스트시 현재 테스트용으로 src 값을 생일축하로 고정)\n\
    -----------------------------------------------------------------\n\
    ---- "API 목록 -> Try it out" 클릭후 입력할 parameter ----\n\
    -----------------------------------------------------------------\n\
    status -> enabled or all 입력\n\
    event_id -> events 테스트 결과로 나온 숫자중 택 1\n\
    how -> formal or informal 입력\n\
    -----------------------------------------------------------------\n')

events = {('1','생일',1),('2','합격',1),('3','입학',1),('4','졸업',1),('5','입사',1),('6','부고',0), ('7','퇴사',0),('8','불합격',0),('9','추석',1),('999','기타',0)}

def none_or_empty(str):
    return (str == None) | (str == '')

def get_dummy_phrase(user_id, friend_id, event_id, keyword):
    if event_id == '1':
        return '생일 축하해'
    elif event_id == '2':
        return '합격 축하해'
    elif event_id == '3':
        return '입학 축하해'
    elif event_id == '4':
        return '졸업 축하해'
    elif event_id == '5':
        return '입사 축하해'
    elif event_id == '9':
        return correct(chuseok_generator.generate())
    elif event_id == '999':
        return keyword + ' 축하해'
    else:
        return 'It is not allowed to generate a phrase for disabled event type'

def post_dummy_phrase(event_id, keyword, src):
    print("문구 저장")
    return True
        
def get_converted(src_list, convert_type, use_corrector):
    
    converted_list = None
    if convert_type == 'formal':
        converted_list = utils.toformal(src_list)
    elif convert_type == 'informal':
        converted_list = utils.toinformal(src_list)
    else:
        converted_list = src

    if use_corrector == True:
        return utils.correct(converted_list)
    else:
        return converted_list


parser = reqparse.RequestParser()
# /phrase/<event_id>?use_cache=[1|0]
parser.add_argument("use_cache", type=int)
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

@api.route('/events/<string:status>')
class Events(Resource):
    
    def get(self, status):
        """ 이벤트 목록을 반환한다 status: <all, enabled, disabled>
        Examples 1: GET /events/all
        Examples 2: GET /events/enabled
        Exmaples 3: GET /events/disabled

        Returns: {'events':[{'event_id':'event_name'}...]}
        """
        return_events = []
        for item in events:
            if (status == 'enabled') & (item[2] == 1):
                return_events.append({item[0]:item[1]})
            elif (status == 'disabled') & (item[2] == 0):
                return_events.append({item[0]:item[1]})
            elif (status == 'all'):
                return_events.append({item[0]:item[1]})
        return {'events':return_events}

@api.route('/phrase/<string:event_id>')
class Phrase(Resource):
    
    def get(self, event_id):
        """이벤트 문구를 반환한다 event_id: 이벤트 종류 id
        Args: user_id/friend_id (Optional): 보내는사람/받는사람, use_cache (Optional): cache 사용 여부 [1|0], default(0), keyword (Optional): event_id가 99(기타)

        Examples 1: GET /phrase/1?user_id=1234&use_cache=1          <- 생일(1), 보내는사람 표시 (O) 받는사람 표시(X), (use_cache=1) 기존에 사용후 저장한 메시지중 택1
        Examples 2: GET /phrase/1?friend_id=4321&use_cache=1        <- 생일(1), 보내는사람 표시 (X) 받는사람 표시(O), (use_cache=1) 기존에 사용후 저장한 메시지중 택1
        Examples 3: GET /phrase/2?use_cache=0                       <- 합격(2), 보내는사람 표시 (X) 받는사람 표시(X), (use_cache=0) 새로 생성한 메시지 반환
        Examples 4: GET /phrase/1?location=seoul&extrainfo=weather  <- 생일(1), 위치정보 사용 시에는 use_cache=1 은 무시된다.

        Returns: {'phrase':'generated sentence for a event'}
        """
        user_id = parser.parse_args()['user_id']
        friend_id = parser.parse_args()['friend_id']
        use_cache = parser.parse_args()['use_cache']
        if use_cache == None:
            use_cache = 0
        key_word = parser.parse_args()['keyword']
        location = parser.parse_args()['location']
        if none_or_empty(location) == False:
            use_cache = 0

        # TODO: user_id , friend_id 문구에 보내는 사람 , 받는 사람 표시가 필요한 경우
        # TODO: use_cache 가 1인 경우 event_id 에 해당하는 문구 중 기존에 생성된 문구를 반환한다. 일단 무시
        print("use_cache:", use_cache)
        return {'phrase': get_dummy_phrase(user_id, friend_id, event_id, key_word)}

    def post(self, event_id):
        """이벤트 문구를 저장한다 event_id: 이벤트 종류 id
        Args: user_id/friend_id (Optional): 보내는사람/받는사람, keyword (optional)
        
        Examples 1: POST /phrase/1?user_id=1234&friend_id=4321&keyword=<소개팅>&src=<기타/소개팅 일때 저장할 문구>
        Examples 2: POST /phrase/2?user_id=1234&friend_id=4321&src=<저장할 문구>
        
        Returns: {'result':'ok | error'}
        """

        # TODO: 저장할 문구에 user_id, friend_id 에 해당하는 이름이 있으면 제거
        user_id = parser.parse_args()['user_id']
        friend_id = parser.parse_args()['friend_id']
        keyword = parser.parse_args()['keyword']
        src = parser.parse_args()['src']
        
        post_dummy_phrase(event_id, keyword, src)

        return {'result':'ok'}

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
    #chuseok_generator = chuseok.ChuseokGenerator()
		
    app.run(debug=True, host='0.0.0.0', port=8000)