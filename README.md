initial python3 enviroment
pip install -r requirements.txt

# LineBot Service deploy

部屬line server

## git struct 
```
.
├── README.md
├── docker
│   ├── Dockerfile
│   ├── build.sh
│   ├── build_from_image
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── dev.env
│   ├── docker-compose.yaml
│   ├── heroku.yml
│   ├── logs
│   │   ├── 2020-07-14-log.log
│   │   ├── 2020-07-15-log.log
│   │   └── 2020-07-16-log.log
│   ├── module
│   │   ├── __pycache__
│   │   ├── app\ copy.py
│   │   ├── const.py
│   │   ├── controller.py
│   │   ├── controller_line.py
│   │   ├── dao.py
│   │   ├── index.html
│   │   ├── linux_chromedriver
│   │   ├── log.py
│   │   ├── mac_chromedriver
│   │   ├── server.py
│   │   ├── service.py
│   │   ├── service_heroku.py
│   │   ├── service_line.py
│   │   └── utils.py
│   └── run.sh
├── heroku.yml
├── logs
└── worker
    ├── Dockerfile
    └── back_heroku.yml
```

## 部屬流程

1. step1: 下載專案
```
git clone ${PROJECT_URL}
```
2. step2: 視情況修改環境變數
```
vi ./docker/dev.env
```
3. step3: run docker image
```
./docker/run.sh 1
```
4. 本機測試直接跑server.py
```
python ./docker/module/server.py
```
- 