# coding: utf-8
import const
from datetime import datetime, timedelta
from opencc import OpenCC
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import datetime
import log as logpy
import re
import utils
import requests
import dao
import pymysql
import json

log = logpy.logging.getLogger(__name__)

class lineService(object):
    def getSoupbyApiChrome(self, url):
        try:
            browser1 = webdriver.Remote(const.CHROMEDRIVER_PATH, DesiredCapabilities.CHROME)
            browser1.get(url)
            soup = BeautifulSoup(browser1.page_source, features='html.parser')
            return soup
        except Exception as e:
            log.error(utils.except_raise(e))
        finally:
            browser1.quit()
    def getSoupbyLocalChrome(self, url):
        try:
            # chromedriver='/usr/local/bin/chromedriver'
            #container alpine linux path
            chromedriver='/usr/bin/chromedriver' 
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920x1080")
            browser = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
            browser.get(url)
            self.soup = BeautifulSoup(browser.page_source, features='html.parser')
            return self.soup
        except Exception as e:
            log.error(utils.except_raise(e))
        finally:
            browser.quit()

    def getForecast(self, CID):
        url='https://www.cwb.gov.tw/V8/C/W/County/County.html?CID='+CID
        response=''
        try:
            # soup = self.getSoupbyApiChrome(url)
            soup = self.getSoupbyLocalChrome(url)
            ths_head=soup.find('div',{"id":"PC_week"}).find('thead').find('tr').find_all('th')
            tbody_week=soup.find('div',{"id":"PC_week"}).find('tbody')
            tds_day=tbody_week.find('tr',{"class":"day"}).find_all('td')
            tds_night=tbody_week.find('tr',{"class":"night"}).find_all('td')
            for i in range(len(ths_head)) :
                response+=('星期' + re.search(r".*<\/span>{1}(.*)<\/span>$", str(ths_head[i].find('span',{"class":"heading_3"}))).group(1) + '\n')
                response+=('白天' + tds_day[i].find('img').get('title') + '\n')
                response+=('晚上' + tds_night[i].find('img').get('title')+ '\n')
        except Exception as e:
            log.error(utils.except_raise(e))
        return response

    def getWeather(self, CID):
        url='https://www.cwb.gov.tw/V8/C/W/County/County.html?CID='+CID
        response=''
        try:
            # soup = self.getSoupbyApiChrome(url)
            soup = self.getSoupbyLocalChrome(url)
            ul_36HR=soup.find('ul',{"id":"36HR_MOD"})
            for li in ul_36HR.find_all('li'):
                response+=(li.find('span',{"class":"title"}).string + '\n')
                response+=(li.find('span',{"class":"tem"}).find('span',{"class":"tem-C is-active"}).string + '°C' + '\n')
                span_rain_rate=li.find('span',{"class":"rain"})
                response+=('降雨率:' + re.search(r".*><\/i>{1}(.*)<\/span>$", str(span_rain_rate)).group(1) + '\n')
        except Exception as e:
            log.error(utils.except_raise(e))
        return response
    
    def getBnbRoomStatus(self, bnbNameList, bnbUrlList):
        resultList=[]
        i=0
        for bnbUrl in bnbUrlList:
            resultStr=''
            resultStr += str(bnbNameList[i]) + "\n"
            i+=1
            response = requests.get(bnbUrl)
            if response.status_code == 200:
                bnbStrList=str(response.text).split("\n")
                for bnbStr in reversed(bnbStrList):
                    regResult=re.search(r"^(SUMMARY:){1}(.*)$",bnbStr)
                    if regResult != None:
                        resultStr += regResult.group(2) + '\n'
                    regResult=re.search(r"^(DTSTART;VALUE=DATE:){1}(.*)$",bnbStr)
                    if regResult != None:
                        resultStr += '開始:' + regResult.group(2) + '\n'
                    regResult=re.search(r"^(DTEND;VALUE=DATE:){1}(.*)$",bnbStr)
                    if regResult != None:
                        resultStr += '結束:'+ regResult.group(2) + '\n'
            resultList.append(resultStr)
        return resultList
    
    def getDbData(self):
        data=[]
        try:
            conn = pymysql.Connect(host=const.DB_HOST,user=const.DB_ACCOUNT,passwd=const.DB_PASSWORD,db=const.DB_DB,charset='utf8')
            data = dao.Database(conn).queryAirBnb(1)
            log.info(len(data))
            result = json.loads(data[0][1])
            log.info(result)
            if len(data) == 1:
                data=result
        except Exception as e:
            log.info("query_airbnb occured some error: " + utils.except_raise(e))
        finally:
            try:
                conn.close()
            except Exception as e:
                log.info("close connection error: " + utils.except_raise(e))

        bnbNameList=[]
        bnbUrlList=[]
        for i in data:
            bnbNameList.append(i.get('room_name'))
            bnbUrlList.append(i.get('room_url'))

        return bnbNameList,bnbUrlList