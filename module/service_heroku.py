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

# class CallApi(object):
def resume_health_check():
    try:
        url = const.RESUME_HEALTH_API
        data = {}
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=json.dumps(data))
        log.info(response.text.encode('utf8'))
        # log.info(json.loads(response.text.encode('utf8')))
    except Exception as e:
        log.error(utils.except_raise(e))
        raise Exception(e)

def avalon_health_check():
    try:
        url = const.AVALON_HEALTH_API
        data = {}
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=json.dumps(data))
        log.info(response.text.encode('utf8'))
        # log.info(json.loads(response.text.encode('utf8')))
    except Exception as e:
        log.error(utils.except_raise(e))
        raise Exception(e)