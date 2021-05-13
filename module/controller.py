# coding=UTF-8
import requests
import json
import time
import re
import ast
import logging
import os
import math
import time
import ctypes 
import threading
import dao
import const
import log as logpy
import pymysql
import service
import utils
import service_line
from datetime import datetime, timedelta
from flask import Flask, Response, render_template, request, redirect, jsonify, send_from_directory, url_for
from threading import Timer,Thread,Event
from flask_restful import Resource
from datetime import datetime
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

log = logpy.logging.getLogger(__name__)

def setup_route(api):
    api.add_resource(Default, '/')
    api.add_resource(HealthCheck, '/healthCheck')
    api.add_resource(BatchStart, '/batchStart')
    api.add_resource(BatchStop, '/batchStop')
    api.add_resource(Transmit, '/transmit')
    api.add_resource(Weather, '/weather')
    api.add_resource(Forecast, '/forecast')
    api.add_resource(SendMail, '/sendmail')
    api.add_resource(airbnb, '/airbnb')
    api.add_resource(Iframe, '/iframe')
    api.add_resource(StaticResource, '/static/<path:filename>')
    api.add_resource(ChatList, '/chatList')

# curl -v -X POST http://localhost:3001/chatList \
# -H 'Content-Type: application/json' -d '{"user":"test","message":"test"}'
class ChatList(Resource):
    def post(self):
        log.info('SetChatList api start')
        args = request.get_json()
        log.info(args)
        return {
            'status': 200,
            'message': 'success',
            'data': service_line.lineService().chatList(args.get('user'),args.get('message'))
        }, 200


class Iframe(Resource):
    log.debug('check health')
    def get(self):
        return send_from_directory('./resource', 'index.html')

class StaticResource(Resource):
    def get(self, filename):
        # root_dir = os.path.dirname(os.getcwd())
        # return send_from_directory( os.path.join(root_dir,'static'), filename)
        return send_from_directory( filename )

class airbnb(Resource):
    def get(self):
        try:
            conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,db=const.DB_DB,charset='utf8')
            data = dao.Database(conn).queryAirBnb(1)
            log.info(len(data))
            result = json.loads(data[0][1])
            log.info(result)
            if len(data) == 1:
                return {'status': 200,'message': 'success','result': result}, 200
            else:
                return {'status': 204,'message': "no data exist"}, 204

        except Exception as e:
            log.info("query_bot_work_list occured some error: " + utils.except_raise(e))
            return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0])}, 500
        finally:
            try:
                conn.close()
            except Exception as e:
                log.info("close connection error: " + utils.except_raise(e))
                return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0])}, 500

    def post(self):
        content_type=request.headers.get('content-type')
        content_type=''.join( i.lower() for i  in content_type.split() )
        log.info(content_type)
        if content_type != 'application/json':
            return {'status': 415,'message':'content type should be [application/json]'}, 415

        receive_json=request.get_json()
        log.info(receive_json)
        if receive_json == None or len(receive_json)==0:
            return {'status': 422,'message':'Error, missing necessary data'}, 422
        for i in receive_json:
            if i.get('room_name') == None or i.get('room_url') == None:
                return {'status': 422,'message':'Error, missing necessary parameter [room_name] or [room_url]'}, 422

        try:
            conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,db=const.DB_DB,charset='utf8')
            update_row = dao.Database(conn).insertAirBnb( json.dumps(receive_json) )
            log.info(update_row)
            # # if update_row != 0:
            return {'status': 200,'message': 'success','result': {'description': "Success, update airbnb with data:" + json.dumps(receive_json)},}, 200
        except Exception as e:
            log.info("query_bot_work_list occured some error: " + utils.except_raise(e))
            return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0])}, 500
        finally:
            try:
                conn.close()
            except Exception as e:
                log.info("close connection error: " + utils.except_raise(e))
                return {'status': 500,'message': "[{}] {}".format(e.__class__.__name__, e.args[0]) }, 500


class SendMail(Resource):
    #localhost:8331/sendmail?receiver=chenhung0506@gmail.com&subject=這是標題&msg=這是內容
    def post(self):
        args = request.get_json()
        return self.process(args)
    def get(self):
        args = request.args
        return self.process(args)
    def process(self,args):
        log.info(args)
        status, result, message = utils.sendEmail(args.get('receiver'),args.get('subject'),args.get('msg'))
        return {
            'status': status,
            'result': result,
            'message': message
        }, status

class Default(Resource):
    def get(self):
        return {
            'status': 200,
            'message': 'health',
            'result': {}
        }, 200

class Weather(Resource):
    def get(self):
        log.info('GetWeather api start')
        lineService = service_line.lineService()
        return {
            'status': 200,
            'message': 'success',
            'result': lineService.getWeather('65')
        }, 200

class Forecast(Resource):
    def get(self):
        log.info('GetWeather api start')
        lineService = service_line.lineService()
        return {
            'status': 200,
            'message': 'success',
            'result': lineService.getForecast('65')
        }, 200


class HealthCheck(Resource):
    log.debug('check health')
    def get(self):
        return {
            'status': 0,
            'message': 'success',
            'method': request.method,
            'username': request.form.get('username'),
            'PHONE_NUMBER': const.PHONE_NUMBER
        }, 200

class BatchStop(Resource):
    def get(self):
        log.info('BatchStop api start')
        return {
            'status': 200,
            'message': utils.stop_batch()
        }, 200

class BatchStart(Resource):
    def get(self):        
        log.info('stop batch:' + utils.stop_batch())
        log.info('BatchStart api start')
        time.sleep(int(5))
        utils.prepare_batch_blocking(transmitProcess,None)
        # utils.prepare_batch_blocking(batchTest,'*/1 * * * *',None)
        
        # sched = BlockingScheduler()
        # sched.add_job(cronTest, CronTrigger.from_crontab(const.TRANSMIT_CRON))
        # sched.start()
        return {
            'message': 'success'
        }, 200

def batchTest():
    log.info(datetime.today().strftime('%Y-%m-%d'))



class Transmit(Resource):
    def get(self):
        return {
            'status': 200,
            'message': transmitProcess(request)
        }, 200

def transmitProcess(request):
    try:
        callApi=service.CallApi()
        dataForRakutens = callApi.getTag(request)
        dataForRakutens = callApi.sortData(dataForRakutens)
        # return dataForRakutens
        log.info("dataForRakuten quantity:" + str(len(dataForRakutens['data'])))
        report=[]
        errorEmail=""
        for val in dataForRakutens['data']:
            dataForRakuten={}
            dataForRakuten['data']=[]
            dataForRakuten['data'].append(val)
            dataForRakuten['total_size']=1
            # return dataForRakuten
            callArmsResponse=callApi.transmitToArms(dataForRakuten)
            if callArmsResponse.status_code == 204 :
                log.info('Transmit success')
                report.append({"session_id":val["session_id"], "message":"success", "status": 200})
            else:
                log.info('Transmit fail, status: ' + str(callArmsResponse.status_code) + ', message: ' + callArmsResponse.text)
                resendUrl='http://' + const.SERVER_IP + ':' + const.PORT + '/transmit?call_direction=outbound&session_id=' + val["session_id"]
                errorEmail = errorEmail + 'transmit error, session id: ' + val["session_id"] + '&nbsp;&nbsp;&nbsp;&nbsp;<a href="' + resendUrl + '"> click here to resend </a><br>'
                report.append({"session_id":val["session_id"], "message":"fail", "status": 204 , "error_data" : dataForRakuten})
        
        
        if errorEmail != "":
            log.info('send error email')
            subject = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d') + "AICC transmit to Arms Alert Mail"
            utils.sendEmail(["chenhung0506@gmail.com", "chenhunglin@emotibot.com"], subject, errorEmail)

        log.info('process complete')

        return report

    except Exception as e:
        log.error("transmitProcess error: "+utils.except_raise(e))
        return utils.except_raise(e)

def transmitProcessTest(request):
    try:
        callApi=service.CallApi()
        callArmsResponse=callApi.transmitToArmsTest()
        if callArmsResponse.status_code == 204 :
            log.info('Transmit success')
            return 'success'
        else:
            log.info('Response status: ' + str(callArmsResponse.status_code) + ', message: ' + callArmsResponse.text)
            return 'fail'
        log.info('process complete')

    except Exception as e:
        log.error("transmitProcess error: "+utils.except_raise(e))

def testGetChatRecords():
    try:
        callApi=service.CallApi()
        # s_reponse=callApi.getChatRecords(request).text.encode('utf8')
        # log.info(s_reponse)
        return callApi.getChatRecords("1eb7c32c-9333-11ea-bbff-119443b68c06")
        
    except Exception as e:
        log.error("transmitProcess error: "+utils.except_raise(e))