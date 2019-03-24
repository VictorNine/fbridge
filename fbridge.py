import json
import requests
from threading import Thread
import toml

from fbchat import log, Client
from fbchat.models import ThreadType, Message 

users = dict()
threads = dict()
revThreads = dict() # Reverse lookup

username = ""
password = ""

## Send message to matterBridge
def sendMsg(username, gateway, text):
    headers = {'content-type': 'application/json'}
    payload = {"text": text,"username":username ,"gateway":gateway}
    r = requests.post('http://localhost:4242/api/message', data=json.dumps(payload), headers=headers)


# Subclass fbchat.Client and override required methods
class FBListener(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        # Don't do anything with messages sendt by you
        if author_id == self.uid:
            return

        self.markAsDelivered(thread_id, message_object.uid)
#        self.markAsRead(thread_id)

        log.info("{} fra: {} - from {} in {}".format(message_object, author_id, thread_id, thread_type.name))

        username = ""
        ## Find the username from author_id
        if author_id in users:
            username = users[author_id]
        else:
            username = author_id

        ## Set a gateway from the thread_id
        gateway = "FBgateway"
        if thread_id in threads:
            gateway = threads[thread_id]

        sendMsg(username, gateway, message_object.text)

def listen(fbClient):
        r = requests.get('http://localhost:4242/api/messages')
        while True:
            r = requests.get('http://localhost:4242/api/stream', stream=True)
            for msg in r.iter_lines():
                if msg:
                    print(msg)
                    jmsg = json.loads(msg)
                    if jmsg["gateway"] == "":
                        continue
                    
                    if jmsg["gateway"] == "FBgateway":
                        sendMsg("bot", "FBgateway", "This gateway is linked to every thread on facebook and can't be used for sending messages.") 
                    else:
                        fbThread = revThreads[jmsg["gateway"]]
                        if len(fbThread) > 10:
                            threadType = ThreadType.GROUP
                        else:
                            threadType = ThreadType.USER

                        fbClient.send(Message(text=jmsg["text"]), thread_id=fbThread, thread_type=threadType)
        r.Close()


def readConfig():
    global username 
    global password
    global revThreads

    ### Load config
    f = open("config.toml", "r")
    toml_string = f.read() 
    parsed_toml = toml.loads(toml_string)
   
    userData = parsed_toml["login"]
    username = userData["username"]
    password = userData["password"]

    th = parsed_toml["threads"]
    us = parsed_toml["users"]

    for key, value in th.items():
        threads[key]=value["gateway"] 

    for key, value in us.items():
        users[key]=value["username"] 

    revThreads = {v: k for k, v in threads.items()}

readConfig()

client = FBListener(username, password)

t = Thread(target = listen, args=(client,))
t.start()

client.listen()
