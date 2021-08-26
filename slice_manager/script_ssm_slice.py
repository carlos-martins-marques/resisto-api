import sys
from tornado import websocket, web, ioloop, httpserver
import json
import logging
import time
import asyncio
import requests
import os
import paramiko

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

names = [ 'access', 'core', 'ue' ]
actions = [ 'registry' , 'start', 'reconfig', 'registration', 'handover', 'add', 'remove' ]
data_a = {}
data_c = {}
data_u = {}
ssmId = {}
access_ssm = 2
ssm = 0
maxSsm = 2 + access_ssm
lock = asyncio.Lock()
liveWebSockets = {}
ueWebSockets = {}
ue_id=2

def getStatus(serviceId):
    status=''
    ip_address = os.environ.get("SONATA_API")
    port = os.environ.get("SONATA_API_PORT")
    #ip_address = "193.136.92.119"
    #port = "32002"
    url = "http://"+ip_address+":"+port+"/api/v3/records/services/"+serviceId
    response = requests.get(url)
    if(response.ok):
        responseDict = json.loads(response.text)
        status = responseDict["status"]
    else:
        LOG.warning("Status request return code: " + str(response.status_code))
        #response.raise_for_status()

    return status

class WSHandler(websocket.WebSocketHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def open(self):
        LOG.info('New connection')


    def on_close(self):
        LOG.info('Connection closed')
        for key, value in liveWebSockets.items():
            if self == value:
                liveWebSockets.pop(key)
                break
        for key, value in ueWebSockets.items():
            if self == value:
                ueWebSockets.pop(key)
                break
    def check_origin(self, origin):
        return True

    
    async def on_message(self, message):
        global data_a
        global data_c
        global data_u
        global ssm
        global ssmId
        global ue_id
        LOG.info('message received:  %s' % message)

        messageDict = json.loads(message)
        name = messageDict['name']
        id = messageDict['id']
        action = messageDict['action']

        LOG.info("Received action: " + action)

        # registry
        if action == actions[0]:
            sfuuid = messageDict['sfuuid']
            ssmId[id]=sfuuid

            liveWebSockets[sfuuid] = self
            
            if name == names[2]:
                ueWebSockets[sfuuid] = self

            # only for test case
            #toSend = messageDict
            #LOG.info("tosend = " + str(toSend))
            #toSendJson = json.dumps(toSend)
            #LOG.info("send new message " + toSendJson)
            #self.write_message(toSendJson)
        # start
        elif action == actions[1]:
            sfuuid=ssmId[id]
            data_m = messageDict['data']

            if name == names[0]:
                async with lock:
                    order = len(data_a) + 1
                    for vnf in data_m:
                        for interface in vnf["ifdata"]:
                            interface.update({'id':id})
                            if vnf["name"] in ["vnf-open5gcorer5-gnb", "vnf-open5gcorer5-upfe", "vnf-open5gcorer5-igwe"]:
                                interface["ifid"] = interface["ifid"][0:5].replace("1",str(order)) + interface["ifid"][5:]

                    data_a[sfuuid]=data_m
            elif name == names[1]:
                for vnf in data_m:
                    for interface in vnf["ifdata"]:
                        interface.update({'id':id})
                data_c[sfuuid]=data_m
                
            else:
                async with lock:
                    order = len(data_u) + 1
                    for vnf in data_m:
                        for interface in vnf["ifdata"]:
                            interface.update({'id':id})
                            if vnf["name"] in ["vnf-open5gcorer5-ue"]:
                                interface["ifid"] = interface["ifid"][0:5].replace("1",str(order)) + interface["ifid"][5:]
                    data_u[sfuuid]=data_m

            # Wait for have the start of all ssm to reconfig
            while (len(data_a) + len(data_c) + len(data_u)) < maxSsm: 
                LOG.info(name + "-" + sfuuid + ": wait start for others ssm")
                await asyncio.sleep(1)

            # Wait for the service be ready
            for sv_id in data_a:
                while True:
                    status = getStatus(sv_id)
                    if status == "normal operation":
                        break
                    LOG.info(name + "-" + sfuuid + ": wait for service access-" + sv_id + " be ready")
                    await asyncio.sleep(5)

            for sv_id in data_c:
                while True:
                    status = getStatus(sv_id)
                    if status == "normal operation":
                        break
                    LOG.info(name + "-" + sfuuid + ": wait for service core-" + sv_id + " be ready")
                    await asyncio.sleep(5)

            for sv_id in data_u:
                while True:
                    status = getStatus(sv_id)
                    if status == "normal operation":
                        break
                    LOG.info(name + "-" + sfuuid + ": wait for service ue-" + sv_id + " be ready")
                    await asyncio.sleep(5)

            LOG.info(name + "-" + sfuuid + ": wait 60 seconds after all services ready")
            await asyncio.sleep(60)

            data_to_send=[]
            for sv_id in data_a:
                data_to_send += data_a[sv_id]
            for sv_id in data_c:
                data_to_send += data_c[sv_id]
            for sv_id in data_u:
                data_to_send += data_u[sv_id]
            toSend = { "name": name, "id": id, "action": actions[2], 
                    "data": data_to_send}
            LOG.info(name + "-" + sfuuid + ": tosend = " + str(toSend))
            toSendJson = json.dumps(toSend)
            LOG.info(name + "-" + sfuuid + ": send new message " + toSendJson)
            self.write_message(toSendJson)
            ssm += 1
            if ssm == maxSsm:
                ssm=0
                data_a={}
                data_c={}
                data_u={}
                ssmId={}
                ue_id=2

        # registration
        elif action == actions[3]:
            #TODO script to activate proxy arp.
            # url:193.136.92.183 u:altice p:ecitla
            #/bin/bash /opt/stack/script_arp_proxy.sh
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('193.136.92.183', username='altice', password='ecitla')

            stdin, stdout, stderr = client.exec_command('/bin/bash /opt/stack/script_arp_proxy.sh')

            for line in stdout:
                LOG.info(line.strip('\n'))

            client.close()

            #TODO 
            for sfuuid in ueWebSockets:
                
                toSend = { "name": "ue", "id": sfuuid, "action": "registration"}
                toSendJson = json.dumps(toSend)
                LOG.info(name + ": send new message to UE SSM" + toSendJson)

                ueWebSockets[sfuuid].write_message(toSendJson)
            # Get the sfuuid of UE and send the message
            #liveWebSockets[sfuuid].write_message(message)

            toSend = { "name": name, "id": id, "action": action, 
                    "message": "Registration OK"}
            LOG.info(name + ": tosend = " + str(toSend))
            toSendJson = json.dumps(toSend)
            LOG.info(name + ": send new message " + toSendJson)
            self.write_message(toSendJson)

        # handover
        elif action == actions[4]:
            #TODO 
            for sfuuid in ueWebSockets:
                
                toSend = { "name": "ue", "id": sfuuid, "action": "handover", 
                    "edge": str(ue_id)}
                toSendJson = json.dumps(toSend)
                LOG.info(name + ": send new message to UE SSM" + toSendJson)

                ueWebSockets[sfuuid].write_message(toSendJson)
            # Get the sfuuid of UE and send the message
            #liveWebSockets[sfuuid].write_message(message)
            if ue_id == 2:
                ue_id = 1
            else:
                ue_id = 2

            # Estimate time for the handover be applied.
            time.sleep(2)

            toSend = { "name": name, "id": id, "action": action, 
                    "message": "Handover OK"}
            LOG.info(name + ": tosend = " + str(toSend))
            toSendJson = json.dumps(toSend)
            LOG.info(name + ": send new message " + toSendJson)
            self.write_message(toSendJson)

        # add
        elif action == actions[5]:
            #TODO
            # Get the sfuuid of service and send the message
            #liveWebSockets[sfuuid].write_message(message)
            toSend = { "name": name, "id": id, "action": action, 
                    "message": "Add OK"}
            LOG.info(name + ": tosend = " + str(toSend))
            toSendJson = json.dumps(toSend)
            LOG.info(name + ": send new message " + toSendJson)
            self.write_message(toSendJson)

        # remove
        elif action == actions[6]:
            #TODO
            # Get the sfuuid of service and send the message
            #liveWebSockets[sfuuid].write_message(message)
            toSend = { "name": name, "id": id, "action": action, 
                    "message": "Remove OK"}
            LOG.info(name + ": tosend = " + str(toSend))
            toSendJson = json.dumps(toSend)
            LOG.info(name + ": send new message " + toSendJson)
            self.write_message(toSendJson)

        else:
            LOG.warning("Action not recognized: " + action)

app_ssm = web.Application([
    (r'/ssm', WSHandler),
])

""" if __name__ == '__main__':


    http_server = httpserver.HTTPServer(app_ssm)
    http_server.listen(4001)
    ioloop.IOLoop.instance().start() """
