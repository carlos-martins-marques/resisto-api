import sys
from tornado import websocket, web, ioloop, httpserver, gen
import json
from queue import Queue
import threading
import asyncio
import logging
import time

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

message_return = ""

class Client():
    
    def __init__(self, url, argv):
        self.url = url       
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.ioloop = ioloop.IOLoop.instance()
        self.connect(argv)
        #PeriodicCallback(self.keep_alive, 20000).start()
        self.ioloop.start()
 
    def message_received(self, message):
        global message_return
        LOG.info('message received...')
        logging.warning("*********************Handling message: "+message)
        
        # Format message
        messageDict = json.loads(message)
        message = messageDict['message']
        message_return = message

    def register(self, argv):
        try:
            
            #toSend = { "name": sv, "id": sv+"_SSM_0", "sfuuid": sv+"_service_id" , "action": "registry" }
            toSend = argv
            toSendJson = json.dumps(toSend)
            LOG.info("Sending register: " + str(toSendJson))
            self.ws.write_message(toSendJson)
        except Exception as e:
            LOG.error("Exception: " + str(e))

    """
    def reply_to_portal(self, name , id, action):
        toSend = {
            "action": "yet to start"
        }

        try:
            toSendJson = json.dumps(toSend)
            LOG.info("Sending reply: " + str(toSendJson))
            self.ws.write_message(toSendJson)
            LOG.info("Finished sending reply.")
        except Exception as e:
            LOG.error("Exception: " + str(e))
    """
             
    @gen.coroutine
    def connect(self, argv=None):

        LOG.info("connecting to websocket..." + self.url)
        logging.warning("*********************Listening to Requests...!")
        connecting = True
        while connecting:
            try:
                self.ws = yield websocket.websocket_connect(self.url)
            except Exception as e:
                LOG.info("connection error")
                LOG.info(e)
                time.sleep(15)
            else:
                LOG.info("connected")
                connecting = False
                if argv:
                    self.register(argv)
                self.run()

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            if msg is not None:
                LOG.info("received message: " + str(msg))
                self.message_received(msg)
                self.ioloop.stop()
                break

def connectPortal(url, argv):
    Client(url, argv)
    LOG.info("FINISHED")
    return message_return

def client_ssm_thread(argv):
    
    url = 'ws://localhost:4001/ssm'
    if len(argv) < 1:   
        LOG.error("Need to include a parameter ")
        sys.exit()

    #t = threading.Thread(target=connectPortal, args=(url,argv), daemon=True)
    #t.start()

    #t.join()
    return connectPortal(url,argv)



