import grpc
import logging
import sys
import os
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict
from datetime import datetime


from bioservice import connect_pb2_grpc
from bioservice import connect_pb2
from bioservice import event_pb2_grpc
from bioservice import event_pb2 

GATEWAY_CA_FILE = 'ca.crt'
GATEWAY_IP = '172.16.20.100'
#GATEWAY_IP = '172.16.20.190'
GATEWAY_PORT = 4000

DEVICE_IP = '172.16.20.200'
DEVICE_PORT = 51211
USE_SSL = False


def testGateway():
  try:
    channel=None
    with open(GATEWAY_CA_FILE, 'rb') as f:
        creds = grpc.ssl_channel_credentials(f.read())
        channel = grpc.secure_channel("{}:{}".format(GATEWAY_IP, GATEWAY_PORT), creds)

    stub1 = connect_pb2_grpc.ConnectStub(channel)
    connInfo = connect_pb2.ConnectInfo(IPAddr=DEVICE_IP, port=DEVICE_PORT, useSSL=USE_SSL)
    devID = stub1.Connect(connect_pb2.ConnectRequest(connectInfo=connInfo)).deviceID
    

    stub = event_pb2_grpc.EventStub(channel)
    events =  stub.GetLog(event_pb2.GetLogRequest(deviceID=devID, startEventID=22000, maxNumOfLog=500))
    dict_obj = MessageToDict(events)['events']
    kk=filter(lambda ob: 'userID' in ob   , dict_obj)
    for x in kk:
      print(datetime.fromtimestamp(x['timestamp']))


    deviceIDs = [devID]
    stub1.Disconnect(connect_pb2.DisconnectRequest(deviceIDs=deviceIDs))

    channel.close()
  except grpc.RpcError as e:
    print(f'Cannot test the device gateway: {e}', flush=True)
    raise   

def quickStart():
  try:
      testGateway()
      print('getway------tested')
  except grpc.RpcError as e:
    print(f'Cannot run the quick start example: {e}')

if __name__ == '__main__':
    logging.basicConfig()
    quickStart()
