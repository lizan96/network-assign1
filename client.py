import logging, sys, json, threading, os
from clientProtocal import *
from globalVariable import *
from socket import *
from clientParser import *

##################################################################################
## useful functions for client
##################################################################################
def sendMessageToServer():
    clientRequest = json.dumps(CLIENT_MESSAGE)
    clientSocket.send(clientRequest)

def receiveMessageFromServer():
    while True:
        try:
            receivedMessage = clientSocket.recv(1024)
            receivedMessageJson = json.loads(receivedMessage)
            displayMessage = receivedMessageJson["DisplayMessage"]
            print displayMessage
            if displayMessage == LOGOUT_MESSAGE:
                os._exit(1)
        except:
            pass

def loginClientProcess(receivedMessage):
    isContinueLoggingIn = True
    keepConnect = True
    for message in receivedMessage:
        receivedMessageJson = json.loads(message)
        desplayMessage = receivedMessageJson["DisplayMessage"]
        try:
            if receivedMessageJson["LoginSuccess"]:
                isContinueLoggingIn = False
            keepConnect = receivedMessageJson["KeepConnect"]
        except:
            pass
        print desplayMessage

        if keepConnect == False:
            sys.exit()
    return receivedMessageJson, isContinueLoggingIn, keepConnect

##################################################################################
##################################################################################

clientSocket = socket(AF_INET, SOCK_STREAM)
serverIP = str(sys.argv[1])
serverPort = int(sys.argv[2])
clientSocket.connect((serverIP, serverPort))

keepConnect = 1
isContinueLoggingIn = True

username = raw_input('Username: ')
password = raw_input('Password: ')
CLIENT_MESSAGE["Action"] = LOGIN
CLIENT_MESSAGE["Username"] = username
CLIENT_MESSAGE["Password"] = password

sendMessageToServer()

receivedMessage = clientSocket.recv(1024)
receivedMessage = receivedMessage.split("/")

receivedMessageJson, isContinueLoggingIn, keepConnect = loginClientProcess(receivedMessage)

while keepConnect and isContinueLoggingIn:
    # if no such user exist, let user input username again
    if receivedMessageJson["LoginStatus"] == LOGIN_NO_SUCH_USER:
        username = raw_input('Username: ')
        CLIENT_MESSAGE["Username"] = username

    # Otherwise, just re-input password
    password = raw_input('Password: ')
    CLIENT_MESSAGE["Password"] = password

    sendMessageToServer()

    receivedMessage = clientSocket.recv(1024)
    receivedMessage = receivedMessage.split("/")

    receivedMessageJson, isContinueLoggingIn, keepConnect = loginClientProcess(receivedMessage)


recv_thread = threading.Thread(target=receiveMessageFromServer)
recv_thread.setDaemon(True)
recv_thread.start()

# After the user successfully log in, start normal send and receive communication between server
while True:
    clientRequest = raw_input('')
    clientRequestJson = parseClientRequest(clientRequest)
    if clientRequestJson["Action"] == INVALID_ACTION:
        print INVALID_COMMAND
        continue
    if clientRequestJson["Action"] == NO_MESSAGE_TO_SEND:
        print NO_MESSGAE_TO_SEND_REPLY
        continue

    sendMessageToServer()

sys.exit()