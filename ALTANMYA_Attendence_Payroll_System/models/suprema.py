import grpc
import logging
import sys
import os
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict  as msgtodic
from datetime import datetime
from . import bioservice

import odoo.exceptions

# import bioservice.connect_pb2
# import bioservice.event_pb2_grpc
# import bioservice.event_pb2

GATEWAY_CA_FILE = 'ca.crt'
#GATEWAY_IP = '172.16.20.37'
#GATEWAY_IP = '172.16.20.190'
GATEWAY_PORT = 4000

# DEVICE_IP = '172.16.20.200'
# DEVICE_PORT = 51211
USE_SSL = False





def download(DEVICE_IP,DEVICE_PORT,from_rec,GATEWAY_IP):
    errocc = False
    atts_rec = None



    try:
        channel =None
        llocation=os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        llocation=os.path.join(llocation,GATEWAY_CA_FILE)

        with open(llocation, "rb") as f:
            creds = grpc.ssl_channel_credentials(f.read())
            channel = grpc.secure_channel("{}:{}".format(GATEWAY_IP, GATEWAY_PORT), creds)

        stub1 = bioservice.connect_pb2_grpc.ConnectStub(channel)
        # print('connection')
        connInfo = bioservice.connect_pb2.ConnectInfo(IPAddr=DEVICE_IP, port=DEVICE_PORT, useSSL=False)
        devID = stub1.Connect(bioservice.connect_pb2.ConnectRequest(connectInfo=connInfo)).deviceID



        stub = bioservice.event_pb2_grpc.EventStub(channel)
        events =  stub.GetLog(bioservice.event_pb2.GetLogRequest(deviceID=devID, startEventID=from_rec, maxNumOfLog=3000))
        # print(events)
        dict_obj = msgtodic(events)['events']
        # print('xxxxxxxxxxxxxxx33333')
        atts_rec  =filter(lambda ob: 'userID' in ob   , dict_obj)
        # for x in atts_rec:
        #     print(str(x['ID'] )+ '------' +str( x['userID'] )+ '-----' + str(datetime.fromtimestamp(x['timestamp'])))

        # print(atts)

        # for x in kk:
        #     print(datetime.fromtimestamp(x['timestamp']))
        # print('After filter')
        deviceIDs = [devID]
        stub1.Disconnect(bioservice.connect_pb2.DisconnectRequest(deviceIDs=deviceIDs))
        channel.close()
        # print('After chanel close')
        # return k
    except Exception as e:
            errocc = True
    finally:
        if errocc:
            if channel:
                channel.close()
                raise odoo.exceptions.Warning("Failed to download from device: " + DEVICE_IP)
            else:
                raise odoo.exceptions.Warning("Failed to connect device: " + DEVICE_IP)
        else:
            return atts_rec