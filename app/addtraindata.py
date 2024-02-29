# 텍스트 파일을 읽는다.
# 유효성검사 target|text 로 시작하는지 
# utf-8 encoding
# nlp_server 의 POST /traindata/event_id 로 POST 한다.
import requests
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name", type=str)
    parser.add_argument("--event_id", type=int)
    args = parser.parse_args()

    if args.file_name == None:
        print("--file_name <filename> needed.")
    if args.event_id == None: 
        print("--event_id <event_id>n needed.")

    with open(args.file_name, "r", encoding='utf-8') as f:
        data = f.read()


    #headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    url = f"http://localhost:8000/traindata/{args.event_id}"
    data = { "data" : f"{data}" }
    print(url)
    print(data)
    response  = requests.post(url, json=data)
    print(response.text)

    

