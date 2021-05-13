import log
import pymysql
import datetime
import json
import const
import utils

log = log.logging.getLogger(__name__)


class Database(object):
    conn = {}
    def __init__(self):
        # log.info(const.DB_PORT)
        # log.info(const.DB_HOST)
        # log.info(const.DB_ACCOUNT)
        # log.info(const.DB_PASSWORD)
        conn = pymysql.Connect(host=const.DB_HOST, port=int(const.DB_PORT), user=const.DB_ACCOUNT, passwd=const.DB_PASSWORD, db='line',charset='utf8')
        self.conn = conn
    def getContackInfo(self,data):
        cursor = self.conn.cursor()
        try:
            log.info(data)
            if data == None:
                log.info(1)
                cursor.execute("select * from `line`.`contact_info`;")
            elif data.get('user'):
                log.info(2)
                cursor.execute("select * from `line`.`contact_info` where user = %s;", (data.get('user')))
            else:
                log.info(3)
                cursor.execute("select * from `line`.`contact_info`;")
            data = []
            log.info(4)
            for row in cursor.fetchall():
                obj = {}
                for i, value in enumerate(row):
                    log.debug(cursor.description[i][0] + ':'+ str(value))
                    obj[cursor.description[i][0]]= value.strftime("%Y/%m/%d %H:%M:%S") if type(value) is datetime.date else str(value)
                data.append(obj)
            # r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
            return data
        except Exception as e:
            log.info( "get contact_info error: " + utils.except_raise(e))
            raise e
        finally:
            cursor.close()
            self.conn.close()

    def addContackInfo(self,data):
        cursor = self.conn.cursor()
        sql = "insert into `line`.`contact_info`  (user, init_date, info) values ( %s, now(),%s )"
        val = (data.get('user'), data.get('info'))
        log.info(val)
        try:
            cursor.execute(sql, val)
            self.conn.commit()
            return True
        except Exception as e:
            log.info("execute sql: '{}' with params: {} failed with {}".format(sql, val, e))
            log.info(cursor._executed)
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
            self.conn.close()

    # def editUniversity(self,data):
    #     cursor = self.conn.cursor()
    #     sql = "UPDATE university.university SET u_name = %s, kind = %s, descri = %s, pdf1_path = %s, pdf2_path = %s, url_path = %s, reward = %s, medal1 = %s, medal2 = %s, medal3 = %s, medal4 = %s, medal5 = %s WHERE u_id = %s"
    #     val = (data.get('u_name'), data.get('kind'), data.get('descri'), utils.clean_filename(data.get('pdf1_path')), utils.clean_filename(data.get('pdf2_path')), data.get('url_path'), data.get('reward'), data.get('medal1'), data.get('medal2'), data.get('medal3'), data.get('medal4'), data.get('medal5'), int(data.get("u_id")))
    #     log.info(val)
    #     try:
    #         cursor.execute(sql, val)
    #         self.conn.commit()
    #         return True
    #     except Exception as e:
    #         log.info("query '{}' with params {} failed with {}".format(sql, val, e))
    #         log.info(cursor._executed)
    #         self.conn.rollback()
    #         raise e
    #     finally:
    #         cursor.close()
    #         self.conn.close()

    # def delUniversity(self,data):
    #     cursor = self.conn.cursor()
    #     sql = "DELETE FROM university.university WHERE u_id = %s"
    #     val = (data.get('u_id'))
    #     try:
    #         cursor.execute(sql, val)
    #         self.conn.commit()
    #         log.info(cursor.rowcount)
    #         return True
    #     except Exception as e:
    #         log.info( "delUniversity error: " + cursor._executed)
    #         raise e
    #     finally:
    #         cursor.close()
    #         self.conn.close()