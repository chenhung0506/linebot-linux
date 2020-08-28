# -*- coding: utf-8 -*-
from flask import Flask
# from flask_cors import CORS
import log as logpy
import re
import os
import const
import controller
import controller_line
import flask_restful
import utils
import unit_test
# import redis
import service_heroku
from flask_restful import Api
from flask_restful import Resource
from datetime import datetime
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

utils.setLogFileName()
log = logpy.logging.getLogger(__name__)

app = Flask(__name__)
api = Api(app)
controller.setup_route(api)
controller_line.setup_route(api)

if __name__=="__main__":
    sched = BackgroundScheduler()
    sched.start()
    sched.add_job(utils.setLogFileName, CronTrigger.from_crontab('59 23 * * *'))
    # sched.add_job(service_heroku.resume_health_check, CronTrigger.from_crontab('5,15,25,35,45,55 * * * *'))
    # sched.add_job(service_heroku.avalon_health_check, CronTrigger.from_crontab('0,10,20,30,40,50 * * * *'))
    # r = redis.StrictRedis(host='localhost', port=6379, db=0)
    # r.set('foo', 'test redis success')
    # log.info(r.get('foo'))

    # sched.add_job(controller.transmitProcess, CronTrigger.from_crontab(const.TRANSMIT_CRON), [None])
    app.run(host="0.0.0.0", port=const.PORT, debug=True, use_reloader=False)

    # unit_test.dateTest()
    # unit_test.insertTest()
    # unit_test.queryTest()
    # unit_test.insertTest()
    # unit_test.downloadFileTest()
    # unit_test.bnbTest()
    # unit_test.insertBnbTest()
    # unit_test.queryAirBnbTest()