import logging, sys, json
from clientProtocal import *
from globalVariable import *


def parseClientRequest(clientRequest):
    request = clientRequest.split()
    try:
        actionRequested = request[0]

        if compareStringCaseInsensitive(actionRequested, "logout"):
            CLIENT_MESSAGE["Action"] = LOGOUT

        elif compareStringCaseInsensitive(actionRequested, "whoelse"):
            CLIENT_MESSAGE["Action"] = WHOELSE

        elif compareStringCaseInsensitive(actionRequested, "whoelsesince"):
            whoelseSinceTime = request[1]
            CLIENT_MESSAGE["Action"] = WHOELSESINCE
            CLIENT_MESSAGE["WhoelseSinceTime"] = whoelseSinceTime

        elif compareStringCaseInsensitive(actionRequested, "broadcast"):
            CLIENT_MESSAGE["Action"] = BROADCAST
            broadcastMessage = ""
            try:
                broadcastMessage = request[1]
                for messageString in request[2:]:
                    broadcastMessage = broadcastMessage + " "+ messageString
            except:
                pass
            CLIENT_MESSAGE["BroadcastMessage"] = broadcastMessage

        elif compareStringCaseInsensitive(actionRequested, "message"):
            CLIENT_MESSAGE["Action"] = MESSAGE
            # extract send message to whom
            try:
                messageToReceivername = request[1]
                CLIENT_MESSAGE["ReceiverName"] = messageToReceivername
            except:
                CLIENT_MESSAGE["Action"] = INVALID_ACTION
            # extract messages
            try:
                message = request[2]
                for messageString in request[3:]:
                    message = message + " "+ messageString
                CLIENT_MESSAGE["Message"] = message
            except:
                CLIENT_MESSAGE["Action"] = NO_MESSAGE_TO_SEND

        elif compareStringCaseInsensitive(actionRequested, "block"):
            CLIENT_MESSAGE["Action"] = BLOCK
            blockUsername = request[1]
            CLIENT_MESSAGE["BlockOrUnblockUserName"] = blockUsername

        elif compareStringCaseInsensitive(actionRequested, "unblock"):
            CLIENT_MESSAGE["Action"] = UNBLOCK
            unblockUsername = request[1]
            CLIENT_MESSAGE["BlockOrUnblockUserName"] = unblockUsername

        else:
            CLIENT_MESSAGE["Action"] = INVALID_ACTION

    except IndexError:
        CLIENT_MESSAGE["Action"] = INVALID_ACTION

    return CLIENT_MESSAGE

def compareStringCaseInsensitive(string1, string2):
    return string1.lower() == string2.lower()