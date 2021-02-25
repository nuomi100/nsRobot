import MiraiConnnect as mirai
import serverAction as action
import json
import time
import requests
import websocket
import pymysql
from serverAction import nsQueue
from sqlConnect import SQLConnect 
try:
    import thread
except ImportError:
    import _thread as thread
try:
    import init
except ImportError:
    print("can not find init file")


miraiURL =init.miraiURL
miraiKey = init.miraiKey
miraiQQ = init.miraiQQ
session='newsession'

def initMirai():
    mirai.setMiraiURL(miraiURL)
    #获取版本
    mirai.getVersion()
    #获取session
    global session
    session=mirai.getAuth(miraiKey=miraiKey)
    #校验sesson并绑定bot
    mirai.verify(botNumber=miraiQQ)
    #开启webSocket
    mirai.startWebSocket()
    #释放sesson
    #mirai.release(miraiURL=miraiURL,session=session,botNumber=miraiQQ)

def on_message(ws, message):
    incomeJson = json.loads(message)
    if incomeJson['messageChain'][1]['type'] == 'Plain':
        incomeQQ = incomeJson['sender']['id']
        incomeMemberName = incomeJson['sender']['memberName']
        incomeGroupChatID=incomeJson['sender']['group']['id']
        incomeMessage = incomeJson['messageChain'][1]['text']
        temp='Get income message from GroupChat {} named {}(QQ:{}) with text: {}'.format(incomeGroupChatID,incomeMemberName,incomeQQ,incomeMessage)
        print(temp)
        action.judge(message=incomeMessage, qid=incomeQQ, name=incomeMemberName, group=incomeGroupChatID, queue=queue)
        #mirai.sendGroupMessage(miraiURL,session,target=incomeGroupChatID,content="got your message!",messageType="TEXT",needAT=1,ATQQ=incomeQQ)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        print('nsRobot Running!')
        time.sleep(1)
    thread.start_new_thread(run, ())

if __name__ == "__main__":
    initMirai()
    wsURL = 'ws://'+init.miraiURL+'/message?sessionKey=' + mirai.session
    db = pymysql.connect(host=init.dbHost, port=init.dbPort, user=init.dbUser,password=init.dbPassword, db=init.dbName, charset=init.dbCharset)
    SQLConnect(db)
    queue = nsQueue()
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url=wsURL,
                            on_message = on_message,
                            on_error = on_error,
                            on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
