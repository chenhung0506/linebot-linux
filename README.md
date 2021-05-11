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

## Linebot richmenu
```
curl -v -X POST https://api.line.me/v2/bot/richmenu \
-H 'Authorization: Bearer {EnSpzk7sQ04AnBwO34YukvfIRF33MeJzwlHuuwH8eCT9rUXLO6wr0fu50TNllOLh+YkK0I8Vjxx2gVllw5Im82OeAvPTc40wS7HLHS6NdcQUazxxS9myCePXHsITe2kqhCCCWHf0o57+HUo364lvqQdB04t89/1O/w1cDnyilFU=}' \
-H 'Content-Type: application/json' \
-d \
'{
    "size": {
      "width": 2500,
      "height": 843
    },
    "selected": false,
    "name": "richmenu-1",
    "chatBarText": "選單1",
    "areas": [
      {
        "bounds": {
          "x": 0,
          "y": 0,
          "width": 833,
          "height": 843
        },
        "action": {
          "type": "message",
          "label": "tool",
          "text": "tool"
        }
      },
      {
        "bounds": {
          "x": 833,
          "y": 0,
          "width": 833,
          "height": 843
        },
        "action": {
          "type": "uri",
          "label": "https://resume.chlin.tk",
          "uri": "https://resume.chlin.tk"
        }
      },
      {
        "bounds": {
          "x": 1666,
          "y": 0,
          "width": 833,
          "height": 843
        },
        "action": {
          "type": "message",
          "label": "請留言",
          "text": "請留言"
        }
      }
   ]
}'
```

```
curl -v -X POST https://api-data.line.me/v2/bot/richmenu/richmenu-87369babb1cd32d3beea956812e5f350/content \
-H "Authorization: Bearer {EnSpzk7sQ04AnBwO34YukvfIRF33MeJzwlHuuwH8eCT9rUXLO6wr0fu50TNllOLh+YkK0I8Vjxx2gVllw5Im82OeAvPTc40wS7HLHS6NdcQUazxxS9myCePXHsITe2kqhCCCWHf0o57+HUo364lvqQdB04t89/1O/w1cDnyilFU=}" \
-H "Content-Type: image/jpeg" \
-T richmenu.png
```

```
curl -v -X POST https://api.line.me/v2/bot/user/all/richmenu/richmenu-87369babb1cd32d3beea956812e5f350 \
-H "Authorization: Bearer {EnSpzk7sQ04AnBwO34YukvfIRF33MeJzwlHuuwH8eCT9rUXLO6wr0fu50TNllOLh+YkK0I8Vjxx2gVllw5Im82OeAvPTc40wS7HLHS6NdcQUazxxS9myCePXHsITe2kqhCCCWHf0o57+HUo364lvqQdB04t89/1O/w1cDnyilFU=}" \
-H 'Content-Type: application/json'

```