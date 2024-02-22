import requests
import json
from datetime import datetime, timedelta

key = 'HDtjDq4AquAGfqE4U+a/Ml72gVhRsilXehPX09IQwxD5aCLtUxiCZ0m9aqTt0yPqQaXpop/XxhXfEeWfgQQRVA=='
url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'

def base_date_time():
    
    base_date = datetime.now().date().strftime('%Y%m%d')
    base_time = datetime.now().strftime('%H').zfill(2)+datetime.now().strftime('%M').zfill(2)
    fcst_time = (datetime.now() + timedelta(hours=1)).strftime('%H').zfill(2)+'00'
    
    if '0210' <= base_time < '0510':
        base_time = '0200'
    elif '0510' <= base_time < '0810':
        base_time = '0500'
    elif '0810' <= base_time < '1110':
        base_time = '0800'
    elif '1110' <= base_time < '1410':
        base_time = '1100'
    elif '1410' <= base_time < '1710':
        base_time = '1400'
    elif '1710' <= base_time < '2010':
        base_time = '1700'
    elif '2010' <= base_time < '2310':
        base_time = '2000'
    elif '2310' <= base_time or base_time < '0210':
        base_date = (datetime.now().date()- timedelta(days=1)).strftime('%Y%m%d')
        base_time = '2300'
        
    
    return base_date, base_time, fcst_time

def weather():
    base_date, base_time, fcst_time = base_date_time()
    params ={'serviceKey' : key, 'pageNo' : '1', 'numOfRows' : '10', 'dataType' : 'JSON', 'base_date' : base_date, 'fcstDate' : base_date, 'base_time' : base_time, 'fcstTime': fcst_time,'nx' : '61', 'ny' : '125' }
    response = requests.get(url, params=params)

    weather_data = response.json()['response']['body']['items']['item']
    for item in weather_data:
        if item['category'] == 'PTY' :
            print(item)
            if item['fcstValue'] in ('1', '4', '5', '6'):
                return '비'
            elif item['fcstValue'] in ('2'):
                return '비/눈'
            elif item['fcstValue'] in ('3','7'):
                return '눈'
            elif item['fcstValue'] in ('0'):
                continue
        if item['category'] == 'SKY':
            if item['fcstValue'] == '1':
                return '맑음'
            elif item['fcstValue'] == '3':
                return '구름 많음'
            elif item['fcstValue'] == '4':
                return '흐림'
            else:
                return '-'
