import log
import utils

log = log.logging.getLogger(__name__)


class Database(object):
    def __init__(self, conn):
        self.conn = conn
    def queryConversation(self,userId):
        cursor = self.conn.cursor()
        try:
            sql = "SELECT * FROM  heroku_d38736f240fb4e6.CONVERSATION WHERE USER_ID = %s ;"
            val = (userId)
            cursor.execute(sql, val)
            return cursor.fetchall()
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)
    
    def insertConversation(self, userId, conversation):
        cursor = self.conn.cursor()
        try:
            sql = "INSERT INTO heroku_d38736f240fb4e6.CONVERSATION (USER_ID,CONVERSATION) values( %s, %s ) ON DUPLICATE KEY UPDATE CONVERSATION=(%s);"
            val = (userId, conversation, conversation)
            try:
                cursor.execute(sql, val)
            except Exception as e:
                log.info("insert '{}' with params {} failed with {}".format(sql, val, e))
                log.info( "\n executed sql: " + cursor._executed)
                self.conn.rollback()
            log.info("insert success userId: " + userId + "conversation: " + conversation)
            self.conn.commit()
            # if cursor.rowcount == 1 and cursor.rowcount == 2:
            #     log.info('insert fail')
            #     self.conn.rollback()
        except Exception as e:
            raise str(e) 

    def insertAirBnb(self, bnb_data):
        cursor = self.conn.cursor()
        try:
            sql = "INSERT INTO heroku_d38736f240fb4e6.AIRBNB (ID, BNB_DATA) values( 1, %s ) ON DUPLICATE KEY UPDATE BNB_DATA=( %s );"
            val = (bnb_data, bnb_data)
            try:
                cursor.execute(sql, val)
            except Exception as e:
                log.info("insert '{}' with params {} failed with {}".format(sql, val, e))
                log.info( "\n executed sql: " + cursor._executed)
                self.conn.rollback()
            log.info("insert success bnb_data: " + bnb_data)
            self.conn.commit()
            return cursor.rowcount
        except Exception as e:
            raise str(e) 

    def queryAirBnb(self, ID):
        cursor = self.conn.cursor()
        try:
            sql = "SELECT * FROM  heroku_d38736f240fb4e6.AIRBNB WHERE ID = %s ;"
            val = (ID)
            cursor.execute(sql, val)
            return cursor.fetchall()
        except Exception as e:
            log.error(utils.except_raise(e))
            raise Exception(e)

    # create table Community.USER_(
    #     U_ID INT NOT NULL AUTO_INCREMENT,
    #     ACCOUNT VARCHAR(100) NOT NULL,
    #     PASSWORD VARCHAR(100) NOT NULL,
    #     PASSWORD_HINT VARCHAR(100) NOT NULL,
    #     NAME VARCHAR(100) NOT NULL,
    #     JOIN_DATE DATE,
    #     PRIMARY KEY ( U_ID )
    # );
    # create table Community.USER_ROLE(
    #     USER_ID INT NOT NULL,
    #     ROLE_ID VARCHAR(10) NOT NULL,
    #     PRIMARY KEY ( USER_ID, ROLE_ID )
    # );


    # create table heroku_d38736f240fb4e6.AIRBNB(
    #      ID INT NOT NULL AUTO_INCREMENT,
    #      BNB_DATA VARCHAR(10000) NOT NULL,
    #      PRIMARY KEY ( ID )
    # );
     