# coding=UTF-8
import requests
import json
import time
import re
import ast
import sys
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
import errno
import dao
import tempfile
import service_line
from argparse import ArgumentParser
from datetime import datetime
from flask import Flask, Response, render_template, request, redirect, jsonify, abort, send_from_directory
from threading import Timer,Thread,Event
from flask_restful import Resource
from datetime import datetime, timedelta
from werkzeug.middleware.proxy_fix import ProxyFix
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import LineBotApiError, InvalidSignatureError

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    MemberJoinedEvent, MemberLeftEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton,
    ImageSendMessage)

log = logpy.logging.getLogger(__name__)

def setup_route(api):
    api.add_resource(Callback, '/callback')

handler = WebhookHandler(const.CHANNEL_SECRET) #channel secret
line_bot_api = LineBotApi(const.CHANNEL_TOKEN) #access token

if line_bot_api is None or handler is None:
    log.info('Specify LINE_CHANNEL_SECRET and LINE_CHANNEL_ACCESS_TOKEN as environment variables.')
    sys.exit(1)

class Callback(Resource):
    log.info('execute api callback')
    def post(self):
        # log.info(request)
        # log.info(request.headers)
        signature = request.headers['X-Line-Signature']
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except LineBotApiError as e:
            log.info("Got exception from LINE Messaging API: %s\n" % e.message)
            for m in e.error.details:
                log.info(m.property + m.message)
            return 'OK'
        except InvalidSignatureError:
            log.info(const.CHANNEL_SECRET)
            log.info(const.CHANNEL_TOKEN)
            abort(400)

        return 'OK'



# https://ithelp.ithome.com.tw/articles/10218874?sc=pt

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=event.message.text))

# get channel_secret and channel_access_token from your environment variable


static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text
    log.info('user json:' + str(event))
    log.info('user message:' + str(event.message.text))
    log.info('userId: ' + str(event.source.user_id))
    chatList=service_line.lineService().chatList(str(event.source.user_id), str(event.message.text))
    
    try:
        log.info(chatList[len(chatList)-1])
        if len(chatList) > 1:
            if chatList[len(chatList)-2] == '請在下則訊息中留言:':
                log.info('success')

    except Exception as e:
        log.info(utils.except_raise(e))
    

    # service_line.lineService().chatList(event.source.user_id, str(event.message.text))


    # data=[]
    # try:
    #     conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
    #     data = dao.Database(conn).queryConversation( str(event.source.user_id) )
    # except Exception as e:
    #     log.info("queryConversation occured some error: "+utils.except_raise(e))
    # finally:
    #     conn.close()
    # # if len(data) == 1:
    # #     if data[0][1] == '':
    # log.info(len(data))


    # try:
    #     conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
    #     dao.Database(conn).insertConversation( str(event.source.user_id), text )
    # except Exception as e:
    #     log.info("insertConversation occured some error: "+utils.except_raise(e))
    # finally:
    #     conn.close()


    if text == 'tool':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='選擇功能:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="今天天氣", text="今天天氣", data="weather")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="一週天氣", text="一週天氣", data="forecast")
                        ),
                        # QuickReplyButton(
                        #     action=PostbackAction(label="寄信", text="寄信", data="sendemail")
                        # ),
                        # QuickReplyButton(
                        #     action=DatetimePickerAction(label="label3",
                        #                                 data="data3",
                        #                                 mode="date")
                        # ),
                        # QuickReplyButton(
                        #     action=CameraAction(label="label4")
                        # ),
                        # QuickReplyButton(
                        #     action=CameraRollAction(label="label5",data="data1")
                        # ),
                        # QuickReplyButton(
                        #     action=LocationAction(label="label6")
                        # ),
                    ])))
    elif text == 'bnb':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='選擇查詢內容:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="打掃", text="打掃", data="clean-room")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="全部", text="全部", data="bnb-all")
                        ),
                    ])))
    elif text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + str(profile.status_message))
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == 'quota':
        quota = line_bot_api.get_message_quota()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='type: ' + quota.type),
                TextSendMessage(text='value: ' + str(quota.value))
            ]
        )
    elif text == 'quota_consumption':
        quota_consumption = line_bot_api.get_message_quota_consumption()
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='total usage: ' + str(quota_consumption.total_usage)),
            ]
        )
    elif text == 'push':
        line_bot_api.push_message(
            event.source.user_id, [
                TextSendMessage(text='PUSH!'),
            ]
        )
    elif text == 'multicast':
        line_bot_api.multicast(
            [event.source.user_id], [
                TextSendMessage(text='THIS IS A MULTICAST MESSAGE'),
            ]
        )
    elif text == 'broadcast':
        line_bot_api.broadcast(
            [
                TextSendMessage(text='THIS IS A BROADCAST MESSAGE'),
            ]
        )
    elif text.startswith('broadcast '):  # broadcast 20190505
        date = text.split(' ')[1]
        log.info("Getting broadcast result: " + date)
        result = line_bot_api.get_message_delivery_broadcast(date)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='Number of sent broadcast messages: ' + date),
                TextSendMessage(text='status: ' + str(result.status)),
                TextSendMessage(text='success: ' + str(result.success)),
            ]
        )
    elif text == 'bye':
        if isinstance(event.source, SourceGroup):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_group(event.source.group_id)
        elif isinstance(event.source, SourceRoom):
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text='Leaving group'))
            line_bot_api.leave_room(event.source.room_id)
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't leave from 1:1 chat"))
    elif text == 'image':
        url = request.url_root + '/static/logo.png'
        log.info("url=" + url)
        line_bot_api.reply_message(
            event.reply_token,
            ImageSendMessage(url, url)
        )
    elif text == 'confirm':
        confirm_template = ConfirmTemplate(text='Do it?', actions=[
            MessageAction(label='Yes', text='Yes!'),
            MessageAction(label='No', text='No!'),
        ])
        template_message = TemplateSendMessage(
            alt_text='Confirm alt text', template=confirm_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'chlin':
        buttons_template = ButtonsTemplate(
            title='chlin album', text='Hello, my buttons', actions=[
                URIAction(label='Go to resume', uri='https://resume-chlin.herokuapp.com'),
                URIAction(label='Go to avalon', uri='https://resume-chlin.herokuapp.com'),
                URIAction(label='Go to iVoting', uri='https://resume-chlin.herokuapp.com'),
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)

    elif text == '功能' or text == '功能區' or text == 'tool':
        log.info(':::' + str(event.source.user_id))
        buttons_template = ButtonsTemplate(
            title='My buttons sample', text='Hello, my buttons', actions=[
                PostbackAction(label='ping', data='ping'),
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ])
        template_message = TemplateSendMessage(
            alt_text='Buttons alt text', template=buttons_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'carousel':
        carousel_template = CarouselTemplate(columns=[
            CarouselColumn(text='hoge1', title='fuga1', actions=[
                URIAction(label='Go to line.me', uri='https://line.me'),
                PostbackAction(label='ping', data='ping')
            ]),
            CarouselColumn(text='hoge2', title='fuga2', actions=[
                PostbackAction(label='ping with text', data='ping', text='ping'),
                MessageAction(label='Translate Rice', text='米')
            ]),
        ])
        template_message = TemplateSendMessage(
            alt_text='Carousel alt text', template=carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'image_carousel':
        image_carousel_template = ImageCarouselTemplate(columns=[
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='datetime',
                                                            data='datetime_postback',
                                                            mode='datetime')),
            ImageCarouselColumn(image_url='https://via.placeholder.com/1024x1024',
                                action=DatetimePickerAction(label='date',
                                                            data='date_postback',
                                                            mode='date'))
        ])
        template_message = TemplateSendMessage(
            alt_text='ImageCarousel alt text', template=image_carousel_template)
        line_bot_api.reply_message(event.reply_token, template_message)
    elif text == 'imagemap':
        pass
    elif text == 'flex':
        bubble = BubbleContainer(
            direction='ltr',
            hero=ImageComponent(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=BoxComponent(
                layout='vertical',
                contents=[
                    # title
                    TextComponent(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    BoxComponent(
                        layout='baseline',
                        margin='md',
                        contents=[
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/gold_star.png'),
                            IconComponent(size='sm', url='https://example.com/grey_star.png'),
                            TextComponent(text='4.0', size='sm', color='#999999', margin='md',
                                          flex=0)
                        ]
                    ),
                    # info
                    BoxComponent(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            BoxComponent(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    TextComponent(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    TextComponent(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=BoxComponent(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction, separator, websiteAction
                    SpacerComponent(size='sm'),
                    # callAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    SeparatorComponent(),
                    # websiteAction
                    ButtonComponent(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        message = FlexSendMessage(alt_text="hello", contents=bubble)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif text == 'flex_update_1':
        bubble_string = """
        {
          "type": "bubble",
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {
                "type": "image",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip3.jpg",
                "position": "relative",
                "size": "full",
                "aspectMode": "cover",
                "aspectRatio": "1:1",
                "gravity": "center"
              },
              {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "Brown Hotel",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#ffffff"
                      },
                      {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png"
                          },
                          {
                            "type": "icon",
                            "size": "sm",
                            "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png"
                          },
                          {
                            "type": "text",
                            "text": "4.0",
                            "size": "sm",
                            "color": "#d6d6d6",
                            "margin": "md",
                            "flex": 0
                          }
                        ]
                      }
                    ]
                  },
                  {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                      {
                        "type": "text",
                        "text": "¥62,000",
                        "color": "#a9a9a9",
                        "decoration": "line-through",
                        "align": "end"
                      },
                      {
                        "type": "text",
                        "text": "¥42,000",
                        "color": "#ebebeb",
                        "size": "xl",
                        "align": "end"
                      }
                    ]
                  }
                ],
                "position": "absolute",
                "offsetBottom": "0px",
                "offsetStart": "0px",
                "offsetEnd": "0px",
                "backgroundColor": "#00000099",
                "paddingAll": "20px"
              },
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "SALE",
                    "color": "#ffffff"
                  }
                ],
                "position": "absolute",
                "backgroundColor": "#ff2600",
                "cornerRadius": "20px",
                "paddingAll": "5px",
                "offsetTop": "10px",
                "offsetEnd": "10px",
                "paddingStart": "10px",
                "paddingEnd": "10px"
              }
            ],
            "paddingAll": "0px"
          }
        }
        """
        message = FlexSendMessage(alt_text="hello", contents=json.loads(bubble_string))
        line_bot_api.reply_message(
            event.reply_token,
            message
        )
    elif text == 'link_token' and isinstance(event.source, SourceUser):
        link_token_response = line_bot_api.issue_link_token(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='link_token: ' + link_token_response.link_token)
            ]
        )
    elif text == 'insight_message_delivery':
        today = datetime.date.today().strftime("%Y%m%d")
        response = line_bot_api.get_insight_message_delivery(today)
        if response.status == 'ready':
            messages = [
                TextSendMessage(text='broadcast: ' + str(response.broadcast)),
                TextSendMessage(text='targeting: ' + str(response.targeting)),
            ]
        else:
            messages = [TextSendMessage(text='status: ' + response.status)]
        line_bot_api.reply_message(event.reply_token, messages)
    elif text == 'insight_followers':
        today = datetime.date.today().strftime("%Y%m%d")
        response = line_bot_api.get_insight_followers(today)
        if response.status == 'ready':
            messages = [
                TextSendMessage(text='followers: ' + str(response.followers)),
                TextSendMessage(text='targetedReaches: ' + str(response.targeted_reaches)),
                TextSendMessage(text='blocks: ' + str(response.blocks)),
            ]
        else:
            messages = [TextSendMessage(text='status: ' + response.status)]
        line_bot_api.reply_message(event.reply_token, messages)
    elif text == 'insight_demographic':
        response = line_bot_api.get_insight_demographic()
        if response.available:
            messages = ["{gender}: {percentage}".format(gender=it.gender, percentage=it.percentage)
                        for it in response.genders]
        else:
            messages = [TextSendMessage(text='available: false')]
        line_bot_api.reply_message(event.reply_token, messages)
    # else:
    #     line_bot_api.reply_message(
    #         event.reply_token, TextSendMessage(text=event.message.text))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title='Location', address=event.message.address,
            latitude=event.message.latitude, longitude=event.message.longitude
        )
    )


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


# Other Message Type
@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save content.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix='file-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '-' + event.message.file_name
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='Save file.'),
            TextSendMessage(text=request.host_url + os.path.join('static', 'tmp', dist_name))
        ])


@handler.add(FollowEvent)
def handle_follow(event):
    log.info("Got Follow event:" + event.source.user_id)
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow(event):
    log.info("Got Unfollow event:" + event.source.user_id)


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    log.info("Got leave event")


@handler.add(PostbackEvent)
def handle_postback(event):
    regResult=re.search(r"(.*):{1}(weather|forecast{1})$",event.postback.data)
    if regResult != None and regResult.group(2) == 'weather':
        reply_txt=service_line.lineService().getWeather(regResult.group(1))
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=reply_txt[0]))
    elif regResult != None and regResult.group(2) == 'forecast':
        reply_txt=service_line.lineService().getWeather(regResult.group(1))
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=''.join(reply_txt)))

    if event.postback.data == 'ping':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='pong'))
    elif event.postback.data == 'datetime_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['datetime']))
    elif event.postback.data == 'date_postback':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.params['date']))
    elif event.postback.data == 'sendemail':
        try:
            messageList=[]
            messageList.append(event.message.text)
            conn = pymysql.Connect(host='us-cdbr-east-02.cleardb.com',user='bdef9ef0984947',passwd='0b65d70f',db='heroku_d38736f240fb4e6',charset='utf8')
            dao.Database(conn).insertConversation( event.source.user_id, json.dumps(messageList) )
        except Exception as e:
            log.info("insertConversation occured some error: "+utils.except_raise(e))
        finally:
            conn.close()
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='輸入收信人email'))
    elif event.postback.data == 'weather' or event.postback.data=='forecast':
        # 65台北 68桃園 10018新竹市 66台中 10002宜蘭
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='選擇城市',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="台北", data="65:" + event.postback.data , text="台北")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="桃園", data="68:" + event.postback.data , text="桃園")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="新竹", data="10018:" + event.postback.data , text="新竹")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="台中", data="66:" + event.postback.data , text="台中")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="宜蘭", data="10002:" + event.postback.data , text="宜蘭")
                        )
                    ])))
    elif event.postback.data == 'clean-room':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text='查看何日:',
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(
                            action=PostbackAction(label="今日", data="clean-room-today" , text="今日")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="明日", data="clean-room-tomorrow", text="明日")
                        ),
                        QuickReplyButton(
                            action=PostbackAction(label="後天", data="clean-room-day-after-tomorrow", text="後天")
                        )
                    ])))
    elif event.postback.data == 'clean-room-today':
        bnbNameList, bnbUrlList=service_line.lineService().getDbData()
        resultList=service_line.lineService().getBnbRoomStatus(bnbNameList,bnbUrlList)
        message=''
        todayDate=datetime.strftime(datetime.now(), '%Y%m%d')
        log.info('search data:' + todayDate)
        for str in resultList:
            regResult=re.search(r"(結束:"+ todayDate +"){1}",str)
            if regResult != None:
                message += str.split("\n")[0] + '、'
        if message == '' : 
            message = todayDate + ' 無房間需打掃'
        else:
            regResult=re.search(r"(.*)(、){1}", message)
            message =  todayDate + '需打掃房間:\n' + regResult.group(1)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    elif event.postback.data == 'clean-room-tomorrow':
        bnbNameList, bnbUrlList=service_line.lineService().getDbData()
        resultList=service_line.lineService().getBnbRoomStatus(bnbNameList,bnbUrlList)
        message=''
        todayDate=datetime.strftime(datetime.now() + timedelta(days=1), '%Y%m%d')
        log.info('search data:' + todayDate)
        for str in resultList:
            regResult=re.search(r"(結束:"+ todayDate +"){1}",str)
            if regResult != None:
                message += str.split("\n")[0] + '、'
        if message == '' : 
            message = todayDate + ' 無房間需打掃'
        else:
            regResult=re.search(r"(.*)(、){1}", message)
            message =  todayDate + '需打掃房間:\n' + regResult.group(1)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    elif event.postback.data == 'clean-room-day-after-tomorrow':
        bnbNameList, bnbUrlList=service_line.lineService().getDbData()
        resultList=service_line.lineService().getBnbRoomStatus(bnbNameList,bnbUrlList)
        message=''
        todayDate=datetime.strftime(datetime.now() + timedelta(days=2), '%Y%m%d')
        log.info('search data:' + todayDate)
        for str in resultList:
            regResult=re.search(r"(結束:"+ todayDate +"){1}",str)
            if regResult != None:
                message += str.split("\n")[0] + '、'
        if message == '' : 
            message = todayDate + ' 無房間需打掃'
        else:
            regResult=re.search(r"(.*)(、){1}", message)
            message =  todayDate + '需打掃房間:\n' + regResult.group(1)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    elif event.postback.data == 'bnb-all':
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
        log.info(bnbNameList)
        log.info(bnbUrlList)

        resultList=service_line.lineService().getBnbRoomStatus(bnbNameList,bnbUrlList)
        testSendMessageList=[]
        for str in resultList:
            testSendMessageList.append(TextSendMessage(text=str))
        line_bot_api.reply_message(event.reply_token, testSendMessageList)
    elif event.postback.data == 'bnb1':
        bnbNameList=["摩斯2"]
        bnbUrlList=["https://www.airbnb.com.tw/calendar/ical/31877747.ics?s=7fd9df4c43a8cc8b991882cc97841e26"]
        for str in service_line.lineService().getBnbRoomStatus(bnbNameList,bnbUrlList):
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=str))

@handler.add(BeaconEvent)
def handle_beacon(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got beacon event. hwid={}, device_message(hex string)={}'.format(
                event.beacon.hwid, event.beacon.dm)))


@handler.add(MemberJoinedEvent)
def handle_member_joined(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text='Got memberJoined event. event={}'.format(
                event)))


@handler.add(MemberLeftEvent)
def handle_member_left(event):
    log.info("Got memberLeft event")

# def quick_reply(event):
#     line_bot_api.reply_message(
#     event.reply_token,
#     TextSendMessage(
#         text='Quick reply',
#         quick_reply=QuickReply(
#             items=[
#                 QuickReplyButton(
#                     action=PostbackAction(label="label1", data="data1")
#                 ),
#                 QuickReplyButton(
#                     action=MessageAction(label="label2", text="text2")
#                 ),
#                 QuickReplyButton(
#                     action=DatetimePickerAction(label="label3",
#                                                 data="data3",
#                                                 mode="date")
#                 ),
#                 QuickReplyButton(
#                     action=CameraAction(label="label4")
#                 ),
#                 QuickReplyButton(
#                     action=CameraRollAction(label="label5")
#                 ),
#                 QuickReplyButton(
#                     action=LocationAction(label="label6")
#                 ),
#             ])))