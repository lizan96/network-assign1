import logging, sys, json
from clientProtocal import *
from globalVariable import *

def parseClientRequest(clientRequest):
    request = clientRequest.split()

    actionRequested = request[0]
    if actionRequested == "logout":
        CLIENT_MESSAGE["Action"] = LOGOUT
    elif actionRequested == "whoelse":
        CLIENT_MESSAGE["Action"] = WHOELSE
    elif actionRequested == "whoelsesince":
        whoelseSinceTime = request[1]
        CLIENT_MESSAGE["Action"] = WHOELSESINCE
        CLIENT_MESSAGE["WhoelseSinceTime"] = whoelseSinceTime
    elif actionRequested == "broadcast":
        CLIENT_MESSAGE["Action"] = BROADCAST
        broadcastMessage = ""
        try:
            broadcastMessage = request[1]
            for messageString in request[2:]:
                broadcastMessage = broadcastMessage + " "+ messageString
        except:
            pass
        CLIENT_MESSAGE["BroadcastMessage"] = broadcastMessage
    elif actionRequested == "message":
        CLIENT_MESSAGE["Action"] = MESSAGE
        try:
            messageToReceivername = request[1]
            CLIENT_MESSAGE["MessageToReceivername"] = messageToReceivername
        except:
            CLIENT_MESSAGE["Action"] = INVALID_ACTION

        try:
            message = request[2]
            for messageString in request[3:]:
                message = message + " "+ messageString
            CLIENT_MESSAGE["Message"] = message
        except:
            CLIENT_MESSAGE["Action"] = NO_MESSAGE_TO_SEND


    else:
        CLIENT_MESSAGE["Action"] = INVALID_ACTION
    return CLIENT_MESSAGE