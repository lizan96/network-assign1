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
    else:
        CLIENT_MESSAGE["Action"] = ACTION_UNKOWN
    return CLIENT_MESSAGE