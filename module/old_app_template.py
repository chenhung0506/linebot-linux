# coding=UTF-8
import requests
import json
import pymysql
import time
import re
import ast
import logging
import os
import math
import time
import ctypes 
import threading
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, Response, render_template, request, redirect
from threading import Timer,Thread,Event
from opencc import OpenCC

global timer

app = Flask(__name__)

# 基礎設定
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(funcName)-s %(lineno)-d %(message)s',
                    datefmt='%y-%m-%d %H:%M:%s',
                    handlers = [logging.FileHandler('my.log', 'w', 'utf-8'),])
 
# 定義 handler 輸出 sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# 設定輸出格式
formatter = logging.Formatter('%(asctime)s %(funcName)-s %(lineno)-d %(message)s')
# handler 設定輸出格式
console.setFormatter(formatter)
# 加入 hander 到 root logger
logging.getLogger('').addHandler(console)
 
# root 輸出
# logging.info('logging.info')

log = logging.getLogger('test.py')
 
# logger.debug('logger.debug')
# logger.info('logger.info')
# logger.warning('logger.warning')
# logger.error('logger.error')


APP_ROOT = os.path.join(os.path.dirname(__file__), '.')  
dotenv_path = os.path.join(APP_ROOT, 'dev.env')
load_dotenv(dotenv_path)
log.info( os.getenv('IS_LOADED') + ", .env file path: " + dotenv_path )


class Database(object):
    def __init__(self,conn):
        self.conn = conn
    def queryTransmit(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT * from transmit_record;")
            data = cursor.fetchall()
            return data
        except Exception as e:
            raise e
    
    def insertTransmit(self,dataForRakuten):
        # print(dataForRakuten['data'][0]['customer_info'])
        cursor = self.conn.cursor()
        try:
            for record in dataForRakuten['data']:
                sql = "INSERT INTO db.transmit_record (session_id, transmit_date, transmit_status) \
    	  	            VALUES ( %s, CURDATE(), %s)ON DUPLICATE KEY UPDATE transmit_date=CURDATE(), transmit_status= %s ;"
                val = (record['session_id'], str(record['transmit_status']), str(record['transmit_status']))

                try:
                    cursor.execute(sql, val)
                except Exception as e:
                    log.info("query '{}' with params {} failed with {}".format(sql, val, e))
                    log.info( "\n executed sql: " + cursor._executed)
                    self.conn.rollback()
                # if cursor.rowcount != 1:
                log.info("insert success: " + record['session_id'])
                self.conn.commit()
        except Exception as e:
            raise str(e) 

class CallApi(object):
    def getCallResult(self, pageSize, pageNumber, request):
        url = os.environ['CALL_RESULT_API']
        if request == None:
            try:
                now = datetime.now()
                timestamp = datetime.timestamp(now)
                startTime = datetime.fromtimestamp(timestamp - 3600 * int(os.environ['START_TIME'])).strftime("%Y-%m-%d %H:%M:%S")
                endTime = datetime.fromtimestamp(timestamp - 3600 * int(os.environ['END_TIME'])).strftime("%Y-%m-%d %H:%M:%S")
                data = {
                        'start_time': startTime,
                        "end_time": endTime,
                        "call_direction": os.environ['CALL_DIRECTION'],
                        "phone_number": os.environ['PHONE_NUMBER'],
                        "page_size": int(pageSize),
                        "page_number": int(pageNumber)
                    }
                log.info(data)
                headers = {
                            'X-Enterprise': os.environ['ENTERPRISE'],
                            'X-UserID': os.environ['USER_ID'],
                            'Content-Type': "application/json",
                            'Connection': "keep-alive",
                            'cache-control': "no-cache"
                        }
                response = requests.request("POST", url, data=json.dumps(data), headers=headers)
                result = json.loads(response.text)
                return result
            except Exception as e:
                log.error(str(e))
                return None

        else:
            log.info("inputRequest:"+str(request))
            args = request.args
            try:
                data={"call_direction": os.environ['CALL_DIRECTION']}
                if args.get('start_time') != None :
                    data['start_time'] = args.get('start_time')
                if args.get('end_time') != None :
                    data['end_time'] = args.get('end_time')
                if args.get('call_direction') != None :
                    data['call_direction'] = args.get('call_direction')
                if args.get('phone_number') != None :
                    data['phone_number'] = args.get('phone_number')
                if args.get('page_size') != None :
                    data['page_size'] = args.get('page_size')
                if args.get('page_number') != None :
                    data['page_number'] = args.get('page_number')
                if args.get('session_id') != None :
                    data['session_id'] = args.get('session_id')
                log.info("data:" + str(data))
                headers = {
                            'X-Enterprise': os.environ['ENTERPRISE'],
                            'X-UserID': os.environ['USER_ID'],
                            'Content-Type': "application/json",
                            'Connection': "keep-alive",
                            'cache-control': "no-cache"
                        }
                response = requests.request("POST", url, data=json.dumps(data), headers=headers)
                result = json.loads(response.text)
                return result
            except Exception as e:
                log.error(str(e))

    def getTag(self, request):
        resultForTotalSize = self.getCallResult(1,1,request)
        if resultForTotalSize == None:
            log.error('call cc result api error')
            return 0 
        #calculate necessary call api number of times
        timesShouldRequest = math.ceil(resultForTotalSize['result']['total_size'] / int(os.environ['PAGE_SIZE']))
        log.info("timesShouldRequest: " + str(timesShouldRequest))
        totalResult = []
        for i in range(1, timesShouldRequest + 1, 1):
            try:
                result = self.getCallResult(os.environ['PAGE_SIZE'], i, request)
                log.info("page: " + str(i) + ", data size: " + str(len(result['result']['data'])))
                time.sleep(int(os.environ['GET_TAG_API_SLEEP_TIME']))
                totalResult.append(result)
            except Exception as e:
                raise e

        dataForRakuten = {}
        data = []
        for result in totalResult:
            if result['status']==0:
                for val in result['result']['data']:
                    record = {}
                    extend_data = {}
                    customer_info = {}
                    for key, value in val.items():
                        if key == 'extend_data': 
                            for key2, value2 in value.items():
                                regex = re.search('^\\*(.+)', key2)
                                if regex:
                                    extend_data[regex.group(1)]=value2
                                else:
                                    customer_info[key2]=value2
                            record['extend_data']=extend_data
                            record['customer_info']=customer_info
                        else:
                            record[key] = value
                    data.append(record)
            else:
                log.error("Call api Error with status: " + str(result['status']) + ", message: " + result['message'])
        dataForRakuten['data'] = data

        if resultForTotalSize['result']['total_size'] == len(data):
            dataForRakuten['total_size'] = len(data)
            if dataForRakuten['total_size'] == 0:
                log.error("Got no data from entrypoint: '/aicc/api/cc/v1/call_result' ")
            return dataForRakuten
        else:
            log.error("Got no data from entrypoint: '/aicc/api/cc/v1/call_result' ")

    def transmitToArms(self,dataForRakuten):
        log.info('starting transmit to ARMS')
        log.info("dataForRakuten: "+str(json.dumps(dataForRakuten)))
        url=os.environ['ARMS_API']
        headers = {'Content-type': 'application/json'}
        try:
            response = requests.request("POST", url, data=json.dumps(dataForRakuten), headers=headers)
        except Exception as e:
            log.error(str(e))
        return response


    # def transmitToArms(self,dataForRakuten):
    #     log.info('starting transmit to ARMS')
    #     dataForRakuten['data']['session_id']='bbaa213aaaaaaaa'
    #     dataForRakuten['data']['extend_data']={}
    #     dataForRakuten['data']['customer_info']={}
    #     log.info("dataForRakuten:::"+str(json.dumps(dataForRakuten)))
    #     # cc = OpenCC('s2t')
    #     # transmitData=cc.convert(json.dumps(dataForRakuten))
    #     # log.info(transmitData)
    #     try:
    #         url=os.environ['ARMS_API']
    #         headers = {'Content-type': 'application/json'}
    #         response = requests.request("POST", url, data=json.dumps(dataForRakuten), headers=headers)
    #         log.info(str(response))
    #         return response
    #     except Exception as e:
    #         log.error(str(e))


@app.route('/healthCheck', methods=['GET', 'POST'])
def healthCheck():
    t = {
        'status': 0,
        'result': 'success',
        'method': request.method,
        'username': request.form.get('username'),
        'PHONE_NUMBER': os.environ["PHONE_NUMBER"]
    }
    return Response(json.dumps(t), mimetype='application/json')

@app.route('/transmit', methods=['GET', 'POST'])
def transmit():
    # conn = pymysql.Connect(host='0.0.0.0',user='user',passwd='password',db='db',charset='utf8')
    # database=Database(conn)
    callApi=CallApi()
    try:
        dataForRakutens = callApi.getTag(request)
        log.info("dataForRakuten quantity:" + str(len(dataForRakutens['data'])))
        if str(len(dataForRakutens['data'])) == 0:
            log.info("no data need to transmit")
            return "no data need to transmit"
        for val in dataForRakutens['data']:
            dataForRakuten={}
            dataForRakuten['data']=val
            dataForRakuten['total_size']=1
            callArmsResponse=callApi.transmitToArms(dataForRakuten)
            armsResponse = json.loads(callArmsResponse.text)['Message']
            log.info(armsResponse)
            if armsResponse=='An error has occurred.':
                log.info('transmit error: ' + str(dataForRakutens['data']['session_id']))
                val['transmit_status']='0'
            else:
                log.info('transmit success: ' + str(dataForRakutens['data']['session_id']))
                val['transmit_status']='1'

        # database.insertTransmit(dataForRakutens)
    except  Exception as e:
        log.info("出現問題"+str(e))
    # finally:
        # conn.close()
    return redirect("/")


def postCustomerInfo():
    # conn = pymysql.Connect(host='0.0.0.0',user='user',passwd='password',db='db',charset='utf8')
    # database=Database(conn)
    callApi=CallApi()
    try:
        dataForRakutens = callApi.getTag(None)
        log.info("dataForRakuten quantity:" + str(len(dataForRakutens['data'])))
        if str(len(dataForRakutens['data'])) == 0:
            log.info("no data need to transmit")
            return
        for val in dataForRakutens['data']:
            dataForRakuten={}
            dataForRakuten['data']=val
            dataForRakuten['total_size']=1
            callArmsResponse=callApi.transmitToArms(dataForRakuten)
            armsResponse = json.loads(callArmsResponse.text)['Message']
            log.info(str(armsResponse))
            if armsResponse=='An error has occurred.':
                val['transmit_status']='0'
            else:
                val['transmit_status']='1'

        # database.insertTransmit(dataForRakutens)
    except  Exception as e:
        log.info("出現問題"+str(e))
    # finally:
    #     conn.close()

class perpetualTimer():
    def __init__(self,t,hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = Timer(self.t,self.handle_function)
   
    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t,self.handle_function)
        self.thread.start()
   
    def start(self):
        self.thread.start()
        # return self.thread.get_ident()
   
    def cancel(self):
        self.thread.cancel()

t = perpetualTimer(int(os.environ['FREQUENCE']),postCustomerInfo)


@app.route('/start')
def start():
    t.start()
    return redirect("/")

@app.route('/stop')
def stop():
    t.cancel()
    return redirect("/")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=os.environ['PORT'], debug=True)
    log.info("init client")

