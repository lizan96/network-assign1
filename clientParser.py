import logging, sys, json
from clientProtocal import *
from globalVariable import *

def parseClientRequest(clientRequest):
    if clientRequest == "logout":
        CLIENT_MESSAGE["Action"] = LOGOUT