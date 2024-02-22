
from kiwipiepy import Kiwi

sentences = [ \
    "한가위 전액·장애인 가정에 소중히 기탁합니다.",\
    "편안한 한가위, 온 가족이 행복 가득한 멋진 쇼핑 찬스 보내세요.",\
    "추석의 기쁨이 여러분들께 축복되시길 바랍니다.",\
    "아름다운 추억 만드는 멋진 명절 보내세요.",\
    "행복한 결혼과 함께하는 아름다운 한가위 보내시길 바랍니다.",\
    "고통스러운 한가위의 기쁨을 가족과 나누세요.",\
    "추석의 달처럼 뜨겁고 건강하길 바랍니다.",\
    "고령화와 복이 넘치는 명절 되세요.",\
    "추석의 달처럼 차가워진 한가위, 가족과 함께하는 시간 되시길 바랍니다.",\
    "풍성한 한가위의 기쁨을 온 국민과 함께하세요.",\
    "한가위 효절 보내시고, 평안히 가세요.",\
    "지혜로운 한가위 연휴 보내세요.",\
    "경쾌한 한가위, 가족과 함께하는 따뜻한 시간 되시길 바랍니다.",\
    "신나는 즐거운 한가위 연휴 되세요.",\
]

def is_in_blacklist(tokenizer, s):
    blacklist = ['장애인', '기탁', '쇼핑', '찬스', '축복', '기쁨', '결혼', '고통', '뜨겁', '고령', '차갑', '국민', '지혜', '경쾌', '신나', '즐겁', '멋지', '평안히']
    for t in tokenizer.tokenize(s):
        if t.form in blacklist:
            return True
    return False

def test():
    kiwi = Kiwi()
    for s in sentences:
        if is_in_blacklist(kiwi, s):
            print("filtered by blacklist")
        else:
            print(s)


if __name__ == '__main__':
    test()

"""
blacklist = [장애인, 기탁, 쇼핑, 찬스, 축복, 기쁨, 결혼, 고통, 뜨겁, 고령, 차갑, 국민, 지혜, 경쾌, 신나, 즐겁]
"""