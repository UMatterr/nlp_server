
from kiwipiepy import Kiwi

sentences = [ 
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