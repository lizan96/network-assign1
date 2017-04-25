import logging, sys, json
from clientProtocal import *
from globalVariable import *

def parseClientRequest(clientRequest):
    if clientRequest == "logout":
        CLIENT_MESSAGE["Action"] = LOGOUT
    else:
        CLIENT_MESSAGE["Action"] = ACTION_UNKOWN
    return CLIENT_MESSAGE