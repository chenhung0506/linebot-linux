import log as logpy
import sys
import traceback
import service
import const
import os
import smtplib, ssl
import pymysql
import dao
import utils
import json
import dao
import pymysql
import requests
import re
import service_line
# import wget
from threading import Timer,Thread,Event
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.combining import OrTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header

log = logpy.logging.getLogger(__name__)

def insertTest():
    try:
        conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
        dao.Database(conn).insertConversation( 'test2', '["test1","test2","test3","test4"]' )
    except Exception as e:
        log.info("insertConversation occured some error: "+utils.except_raise(e))
    finally:
        conn.close()

def queryTest():
    data=[]
    try:
        conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
        data = dao.Database(conn).queryConversation( 'test2' )
        log.info(len(data))
        log.info(json.loads(data[0][1])[0])
            # print "%s, %s" % (row["USER_ID"], row["CONVERSATION"])
            # log.info (row["USER_ID"] + row["CONVERSATION"])
    except Exception as e:
        log.info("queryConversation occured some error: "+utils.except_raise(e))
    finally:
        conn.close()
    log.info(len(data))

def insertSqlTest():
    try:
        messageList=[]
        messageList.append('test')
        conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
        dao.Database(conn).insertConversation( 'str(event.source.user_id)', str(json.dumps(messageList)) )
    except Exception as e:
        log.info("insertConversation occured some error: "+utils.except_raise(e))
    finally:
        conn.close()
    print(type(json.dumps(messageList)))

# def wgetFileTest():
    # url = 'https://docs.google.com/spreadsheets/d/1gWqUuHMhPaNTs3owkg_ZYI0fRi2gutcRvB3VRnoHIV8/edit#gid=1684370537'
    # wget.download(url, './airBnB_file/facebook.ics')



def downloadFileTest():
    try:
        if not os.path.exists('./airBnB_file'):
            os.makedirs('./airBnB_file')
    except OSError as e:
        print(e)
    url = 'https://docs.google.com/spreadsheets/d/1gWqUuHMhPaNTs3owkg_ZYI0fRi2gutcRvB3VRnoHIV8/edit#gid=1684370537'
    r = requests.get(url, allow_redirects=True)
    open('./airBnB_file/facebook.ics', 'wb').write(r.content)

    # url = 'http://google.com/favicon.ico'
    # r = requests.get(url, allow_redirects=True)
    # log.info(r.headers.get('content-disposition'))
    # filename = getFilename_fromCd(r.headers.get('content-disposition'))
    # open(filename, 'wb').write(r.content)


def getFilename_fromCd(cd):
    #Get filename from content-disposition
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0]

def bnbTest():
    bnbNameList=["摩斯2","康定102","康定103","康定105"]
    bnbUrlList=["https://www.airbnb.com.tw/calendar/ical/31877747.ics?s=7fd9df4c43a8cc8b991882cc97841e26","https://www.airbnb.com.tw/calendar/ical/36770090.ics?s=eae577ab186b34518736abf944d3b53b","https://www.airbnb.com.tw/calendar/ical/31139580.ics?s=37208479f7454e72314f0cb6fa42d431","https://www.airbnb.com.tw/calendar/ical/27663741.ics?s=986d81e1f345327bc9e9cb4025153259"]
    resultList=service_line.lineService().getBnbRoomStatus(bnbNameList,bnbUrlList)
    message=''
    todayDate=datetime.strftime(datetime.now(), '%Y%m%d')
    log.info('search data:' + todayDate)
    for str in resultList:
        regResult=re.search(r"(結束:"+ todayDate +"){1}",str)
        if regResult != None:
            message += str.split("\n")[0] + '=>' + regResult.group(1) + '\n'
    if message == '' : message= '今日無房間需打掃'
    log.info(message)

def bnbDbTest():
    bnbNameList=["摩斯2","康定102","康定103","康定105"]
    bnbUrlList=["https://www.airbnb.com.tw/calendar/ical/31877747.ics?s=7fd9df4c43a8cc8b991882cc97841e26","https://www.airbnb.com.tw/calendar/ical/36770090.ics?s=eae577ab186b34518736abf944d3b53b","https://www.airbnb.com.tw/calendar/ical/31139580.ics?s=37208479f7454e72314f0cb6fa42d431","https://www.airbnb.com.tw/calendar/ical/27663741.ics?s=986d81e1f345327bc9e9cb4025153259"]
    resultList=service_line.lineService().getBnbRoomStatus(bnbNameList,bnbUrlList)
    message=''
    todayDate=datetime.strftime(datetime.now(), '%Y%m%d')
    log.info('search data:' + todayDate)
    for str in resultList:
        regResult=re.search(r"(結束:"+ todayDate +"){1}",str)
        if regResult != None:
            message += str.split("\n")[0] + '=>' + regResult.group(1) + '\n'
    if message == '' : message= '今日 '+ todayDate + ' 無房間需打掃'
    log.info( "message: " + message )

def insertBnbTest():
    try:
        messageList=[]
        messageList.append('test')
        conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
        dao.Database(conn).insertAirBnb( str(json.dumps('{"data":[{"room_name":"摩斯2","room_url":"https://www.airbnb.com.tw/calendar/ical/31877747.ics?s=7fd9df4c43a8cc8b991882cc97841e26"},{"room_name":"摩斯2","room_url":"https://www.airbnb.com.tw/calendar/ical/31877747.ics?s=7fd9df4c43a8cc8b991882cc97841e26"},{"room_name":"摩斯2","room_url":"https://www.airbnb.com.tw/calendar/ical/31877747.ics?s=7fd9df4c43a8cc8b991882cc97841e26"}]}')) )
    except Exception as e:
        log.info("insertBnbTest occured some error: "+utils.except_raise(e))
    finally:
        conn.close()
    print(type(json.dumps(messageList)))

def queryAirBnbTest():
    data=[]
    try:
        conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
        data = dao.Database(conn).queryAirBnb( 1 )
        log.info(len(data))
        log.info(data[0][1])
        log.info(json.loads(data[0][1]))
    except Exception as e:
        log.info("queryAirBnb occured some error: "+utils.except_raise(e))
    finally:
        conn.close()
    log.info(len(data))

def dateTest():
    todayDate=datetime.strftime(datetime.now() - timedelta(days=1) , '%Y%m%d')
    log.info('search data:' + todayDate)