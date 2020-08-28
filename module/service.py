import const
from datetime import datetime, timedelta
from opencc import OpenCC
import re
import log
import json
import requests
import math
import time
import utils
import uuid 

log = log.logging.getLogger(__name__)

class CallApi(object):
    def getCallResult(self, pageSize, pageNumber, request):
        try:
            data={}
            if request == None:
                # now = datetime.now()
                # timestamp = datetime.timestamp(now)
                # startTime = datetime.fromtimestamp(timestamp - 3600 * int(const.START_TIME)).strftime("%Y-%m-%d %H:%M:%S")
                # endTime = datetime.fromtimestamp(timestamp - 3600 * int(const.END_TIME)).strftime("%Y-%m-%d %H:%M:%S")
                startTime = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d') + ' 00:00:00'
                endTime = datetime.strftime(datetime.now(), '%Y-%m-%d') + ' 00:00:00'
                log.info("startTime: " + startTime + ", endTime: " + endTime)
                data = {
                         "start_time": startTime,
                         "end_time": endTime,
                         "call_direction": const.CALL_DIRECTION,
                         "phone_number": const.PHONE_NUMBER,
                         "page_size": int(pageSize),
                         "page_number": int(pageNumber)
                       }
            else:
                log.info("inputRequest:"+str(request))
                args = request.args
                # if args.get('page_size') == None : raise Exception("necessary param 'page_size'")

                data={"call_direction": const.CALL_DIRECTION}
                data['page_size']=int(pageSize)
                if args.get('start_time') != None : data['start_time'] = args.get('start_time')
                if args.get('end_time') != None : data['end_time'] = args.get('end_time')
                if args.get('call_direction') != None : data['call_direction'] = args.get('call_direction')
                if args.get('phone_number') != None : data['phone_number'] = args.get('phone_number')
                if args.get('page_number') != None : data['page_number'] = int(args.get('page_number'))
                if args.get('session_id') != None : data['session_id'] = args.get('session_id')
                # if args.get('page_size') != None : data['page_size'] = int(args.get('page_size'))
                log.info("one times get tag")

            headers = {
                        'X-Enterprise': const.ENTERPRISE,
                        'X-UserID': const.USER_ID,
                        'Content-Type': "application/json",
                        'Connection': "keep-alive",
                        'cache-control': "no-cache"
                      }
            log.info("call api: " + const.GET_TAG_API + "\nwith data: " + str(data))
            response = requests.request("POST", const.GET_TAG_API, data=json.dumps(data), headers=headers)
            if response.status_code != 200:
                raise Exception('Response status: ' + str(response.status_code) + ', message: ' + response.text)
            return json.loads(response.text)
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)

    def getChatRecords(self, uuid):
        url = const.GET_ASR_RESULT_API
        log.info(uuid)
        data = {"uuid": [uuid]}
        headers = {
            'X-Enterprise': const.ENTERPRISE,
            'Content-Type': 'application/json'
        }
        response = requests.request("POST", url, data=json.dumps(data), headers=headers)
        return json.loads(response.text)

    def getTag(self, request):
        resultForTotalSize = self.getCallResult(1,1,request)
        #calculate necessary call api number of times
        totalSize=resultForTotalSize['result']['total_size']
        log.info("total_size:" + str(totalSize))
        totalResult = []
        if totalSize==0 :
            return totalResult
        try:
            result = self.getCallResult(totalSize, 1, request)
            if result['status']!=0:
                return("Call api: " + const.GET_TAG_API + ", got wrong status: " + str(result['status']) + ", message: " + result['message'])
            for val in result['result']['data']:
                totalResult.append(val)
        except Exception as e:
            raise e
        log.debug(totalResult)
        return totalResult
        # page_size = 0
        # if request == None:
        #     page_size=const.PAGE_SIZE
        # else:
        #     page_size=request.args.get("page_size")

        # timesShouldRequest = math.ceil(int(totalSize) / int(page_size))

        # log.info("timesShouldRequest: " + str(timesShouldRequest))
        # totalResult = []
        # if timesShouldRequest==0 :
        #     return totalResult
        # for i in range(1, timesShouldRequest + 1, 1):
        #     try:
        #         result = self.getCallResult(page_size, i, request)
        #         if result['status']!=0:
        #             return("Call api: " + const.GET_TAG_API + ", got wrong status: " + str(result['status']) + ", message: " + result['message'])
        #         log.info("page: " + str(i) + ", data size: " + str(len(result['result']['data'])))
        #         time.sleep(int(const.GET_TAG_API_SLEEP_TIME))
        #         for val in result['result']['data']:
        #             totalResult.append(val)
        #     except Exception as e:
        #         raise e



    def sortData(self, tagResults):
        cc=OpenCC('s2t')
        # resultForTotalSize = self.getCallResult(1,1,None)
        dataForRakuten = {}
        sortedData = []

        for record in tagResults:
            extend_data = []
            customer_info = []
            record_session_id = record['session_id']

            #獲取 asr result 開始
            asr_result = self.getChatRecords(record_session_id)
            if asr_result['status']!=0:
                return ("Call api: " + const.GET_ASR_RESULT_API + ", got wrong status: " + str(asr_result['status']) + ", message: " + asr_result['message'])
            record['asr_result']=json.loads(cc.convert(json.dumps(asr_result['result']['data'])))
            #獲取 asr result 結束

            log.debug(record['extend_data'])
            for key, value in record['extend_data'].items():
                regex = re.search('^\\*(.+)', key)
                if regex:
                    extend_data.append({"session_id":record_session_id,"col_name":cc.convert(regex.group(1)),"value":cc.convert(value)})
                    # extend_data[cc.convert(regex.group(1))]=cc.convert(value)
                else:
                    customer_info.append({"session_id":record_session_id,"col_name":cc.convert(key),"value":cc.convert(value)})
                    # customer_info[cc.convert(key2)]=cc.convert(value2)
            record['extend_data']=extend_data
            record['customer_info']=customer_info
            sortedData.append(record)

        dataForRakuten['data'] = sortedData

        return dataForRakuten

    def transmitToArms(self,dataForRakuten):
        # dataForRakuten['data'][0]['session_id'] = str(uuid.uuid4())
        log.info(dataForRakuten['data'][0]['session_id'])
        log.debug(json.dumps(dataForRakuten))

        # dataForRakuten['data'][0]['session_id'] = str(uuid.uuid4())
        # dataForRakuten['data'][0]['asr_result']=[{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","taskengine_session_id":"73007cd1-ef05-41ef-a051-72fa7775c293","user_id":"0919040448","user_q":".","score":100,"std_q":"","log_time":"2020-05-11 10:57:40","emotion":"中性","emotion_score":80,"intent":"","intent_score":0,"module":"task_engine","source":"","answer":"[[520.raw]]","raw_answer":"[{\"type\":\"text\",\"subType\":\"text\",\"value\":\"[[520.raw]]\",\"data\":[]}]","faq_cat_name":"","faq_robot_tag_name":"","feedback":"","custom_feedback":"","feedback_time":"","threshold":0,"tspan":139,"id":"37db5df14ec94190a035ffb5082537fe","is_marked":"false","is_ignored":"false"}]
        # dataForRakuten['data'][0]['extend_data']=[{"session_id": "1eb7c32c-9333-11ea-1234-119443b68c06","col_name": "同意二次聯繫","value": "-234/234"},{"session_id": "1eb7c32c-9333-11ea-1234-119443b68c06","col_name": "同意二次聯繫","value": "-234/234"}]
        # new_uuid = str(uuid.uuid4())
        # dataForRakuten['data'][0]['session_id'] = new_uuid
        # for val in dataForRakuten['data'][0]['asr_result']:
        #     val['session_id']=new_uuid
        # for val in dataForRakuten['data'][0]['customer_info']:
        #     val['session_id']=new_uuid
        # for val in dataForRakuten['data'][0]['extend_data']:
        #     val['session_id']=new_uuid

        # log.info(dataForRakuten)
        try:
            response = requests.request("POST", url=const.ARMS_API, data=json.dumps(dataForRakuten), headers={'Content-type': 'application/json'})
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)
        return response

    def transmitToArmsTest(self):
        dataForRakutenTest={"data":[{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","call_direction":"outbound","caller":"07010110688","callee":"0919040448","status":1,"calls_number":1,"talk_start_time":"2020-05-11 10:57:24","ring_duration":5,"talk_duration":18,"asr_result":[{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","taskengine_session_id":"73007cd1-ef05-41ef-a051-72fa7775c293","user_id":"0919040448","user_q":".","score":100,"std_q":"","log_time":"2020-05-11 10:57:40","emotion":"中性","emotion_score":80,"intent":"","intent_score":0,"module":"task_engine","source":"","answer":"[[520.raw]]","raw_answer":"[{\"type\":\"text\",\"subType\":\"text\",\"value\":\"[[520.raw]]\",\"data\":[]}]","faq_cat_name":"","faq_robot_tag_name":"","feedback":"","custom_feedback":"","feedback_time":"","threshold":0,"tspan":139,"id":"37db5df14ec94190a035ffb5082537fe","is_marked":"false","is_ignored":"false"},{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","taskengine_session_id":"73007cd1-ef05-41ef-a051-72fa7775c293","user_id":"0919040448","user_q":"M0","score":100,"std_q":"","log_time":"2020-05-11 10:57:24","emotion":"中性","emotion_score":80,"intent":"","intent_score":0,"module":"task_engine","source":"","answer":"[[520.raw]]testtest您好，這裏是樂天銀行信用卡，您本期信用卡帳單已過期限，請於今日立即繳納年月帳款，以避免有違約金，及利息產生，如您已繳納，請無需理會。","raw_answer":"[{\"type\":\"text\",\"subType\":\"text\",\"value\":\"[[520.raw]]testtest您好，這裏是樂天銀行信用卡，您本期信用卡帳單已過期限，請於今日立即繳納年月帳款，以避免有違約金，及利息產生，如您已繳納，請無需理會。\",\"data\":[]}]","faq_cat_name":"","faq_robot_tag_name":"","feedback":"","custom_feedback":"","feedback_time":"","threshold":0,"tspan":133,"id":"bd211408c29b446e96e0591bb145934e","is_marked":"false","is_ignored":"false"}],"extend_data":[{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","col_name":"同意二次聯繫","value":"無"},{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","col_name":" 客戶已繳款","value":"有表示"},{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","col_name":" 客戶本人接聽","value":"yes"}],"customer_info":[{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","col_name":"01.帳單月份","value":"test"},{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","col_name":"02.名字","value":"test"},{"session_id":"1eb7c32c-9333-11ea-6634-119443b68c06","col_name":"03.身分證號","value":"test"}]}],"total_size":1}
        # dataForRakutenTest={"data":[{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","call_direction":"outbound","caller":"07010110688","callee":"0919040448","status":1,"calls_number":1,"talk_start_time":"2020-05-11 10:57:24","ring_duration":5,"talk_duration":18,"asr_result":[{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","taskengine_session_id":"73007cd1-ef05-41ef-a051-72fa7775c293","user_id":"0919040448","user_q":".","score":100,"std_q":"","log_time":"2020-05-11 10:57:40","emotion":"中性","emotion_score":80,"intent":"","intent_score":0,"module":"task_engine","source":"","answer":"[[520.raw]]","raw_answer":"[{\"type\":\"text\",\"subType\":\"text\",\"value\":\"[[520.raw]]\",\"data\":[]}]","faq_cat_name":"","faq_robot_tag_name":"","feedback":"","custom_feedback":"","feedback_time":"","threshold":0,"tspan":139,"id":"37db5df14ec94190a035ffb5082537fe","is_marked":"false","is_ignored":"false"},{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","taskengine_session_id":"73007cd1-ef05-41ef-a051-72fa7775c293","user_id":"0919040448","user_q":"M0","score":100,"std_q":"","log_time":"2020-05-11 10:57:24","emotion":"中性","emotion_score":80,"intent":"","intent_score":0,"module":"task_engine","source":"","answer":"[[520.raw]]testtest您好，這裏是樂天銀行信用卡，您本期信用卡帳單已過期限，請於今日立即繳納年月帳款，以避免有違約金，及利息產生，如您已繳納，請無需理會。","raw_answer":"[{\"type\":\"text\",\"subType\":\"text\",\"value\":\"[[520.raw]]testtest您好，這裏是樂天銀行信用卡，您本期信用卡帳單已過期限，請於今日立即繳納年月帳款，以避免有違約金，及利息產生，如您已繳納，請無需理會。\",\"data\":[]}]","faq_cat_name":"","faq_robot_tag_name":"","feedback":"","custom_feedback":"","feedback_time":"","threshold":0,"tspan":133,"id":"bd211408c29b446e96e0591bb145934e","is_marked":"false","is_ignored":"false"}],"extend_data":[{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","col_name":"同意二次聯繫","value":"無"},{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","col_name":" 客戶已繳款","value":"有表示"},{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","col_name":" 客戶本人接聽","value":"yes"}],"customer_info":[{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","col_name":"01.帳單月份","value":"test"},{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","col_name":"02.名字","value":"test"},{"session_id":"1eb7c32c-9333-11ea-bbff-119443b68c06","col_name":"03.身分證號","value":"test"}]}],"total_size":1}
        # dataForRakutenTest={"data":[{"session_id":"2213c-w123eww-11ea-85dsf-7df51143b","call_direction":"outbound","caller":"07010110688","callee":"0919040448","status":0,"calls_number":1,"talk_start_time":"2020-01-17 22:03:46","ring_duration":5,"talk_duration":48,"extend_data":{"123":"123"},"customer_info":{}}],"total_size":1}
        new_uuid = str(uuid.uuid4())
        dataForRakutenTest['data'][0]['session_id'] = new_uuid
        for val in dataForRakutenTest['data'][0]['asr_result']:
            val['session_id']=new_uuid
        for val in dataForRakutenTest['data'][0]['customer_info']:
            val['session_id']=new_uuid
        for val in dataForRakutenTest['data'][0]['extend_data']:
            val['session_id']=new_uuid
        log.info(dataForRakutenTest)
        log.info(dataForRakutenTest['data'][0]['session_id'])

        try:
            response = requests.request("POST", url=const.ARMS_API, data=json.dumps(dataForRakutenTest), headers={'Content-type': 'application/json'})
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)
        return response