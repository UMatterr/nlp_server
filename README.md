## nlp backend server 

### Powered by Python/Flask/Pytorch

Project structure:
```
.
├── compose.yaml
├── app
    ├── Dockerfile
    ├── requirements.txt
    └── app.py

```

[_compose.yaml_](compose.yaml)
```
services: 
  web: 
    build:
     context: app
     target: builder
    ports: 
      - '8000:8000' 
```

## Deploy with docker compose ( when you test on your local PC )

```
$ docker compose up -d
[+] Building 1.1s (16/16) FINISHED
 => [internal] load build definition from Dockerfile                                                                                                                                                                                       0.0s
    ...                                                                                                                                         0.0s
 => => naming to docker.io/library/flask_web                                                                                                                                                                                               0.0s
[+] Running 2/2
 ⠿ Network flask_default  Created                                                                                                                                                                                                          0.0s
 ⠿ Container flask-web-1  Started
```

## Expected result with docker compose

Listing containers must show one container running and the port mapping as below:
```
$ docker compose ps
NAME                COMMAND             SERVICE             STATUS              PORTS
flask-web-1         "python3 app.py"    web                 running             0.0.0.0:8000->8000/tcp
```

After the application starts, navigate to `http://localhost:8000` in your web browser


Stop and remove the containers
```
$ **docker compose down**
```
## Deploy with docker compose ( when you test on a remote server )

```
$ docker pull quickerj/umatter
$ docker run -p 80:8000 quickerj/umatter
```

## Expected result with docker compose

Listing containers must show one container running and the port mapping as below:
```
$ docker ps
CONTAINER ID   IMAGE              COMMAND            CREATED        STATUS                                                                                                                     PORTS                                   NAMES
5af56732dec4   quickerj/umatter   "python3 app.py"   16 hours ago   Up 16 hours                                                                                                                0.0.0.0:80->8000/tcp, :::80->8000/tcp   beautiful_leavitt

```

After the application starts, navigate to `http://<Public IP of EC2>:8000` in your web browser


Stop and remove the containers
```
$ docker kill 5af56732dec4
```
