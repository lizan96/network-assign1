import logging, sys, json, threading
from clientProtocal import *
from globalVariable import *
from socket import *
from clientParser import *
import select

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

clientRequest = json.dumps(CLIENT_MESSAGE)
clientSocket.send(clientRequest)

receivedMessage = clientSocket.recv(1024)
receivedMessageJson = json.loads(receivedMessage)
desplayMessage = receivedMessageJson["DisplayMessage"]
if receivedMessageJson["LoginSuccess"]:
    isContinueLoggingIn = False
keepConnect = receivedMessageJson["KeepConnect"]
print desplayMessage

while keepConnect and isContinueLoggingIn:
    if receivedMessageJson["LoginStatus"] == LOGIN_NO_SUCH_USER:
        username = raw_input('Username: ')
        CLIENT_MESSAGE["Username"] = username
    password = raw_input('Password: ')
    CLIENT_MESSAGE["Password"] = password

    clientRequest = json.dumps(CLIENT_MESSAGE)
    clientSocket.send(clientRequest)

    receivedMessage = clientSocket.recv(1024)
    receivedMessageJson = json.loads(receivedMessage)
    desplayMessage = receivedMessageJson["DisplayMessage"]
    if receivedMessageJson["LoginSuccess"]:
        isContinueLoggingIn = False
    keepConnect = receivedMessageJson["KeepConnect"]
    print desplayMessage
    # if not keepConnect:
    #     sys.exit()

def receiveMessageFromServer():
    while True:
        try:
            receivedMessage = clientSocket.recv(1024)
            receivedMessageJson = json.loads(receivedMessage)
            desplayMessage = receivedMessageJson["DisplayMessage"]
            print desplayMessage
        except:
            pass

recv_thread = threading.Thread(target=receiveMessageFromServer)
recv_thread.setDaemon(True)
recv_thread.start()


while True:
    clientRequest = raw_input('')
    clientRequestJson = parseClientRequest(clientRequest)
    if clientRequestJson["Action"] == INVALID_ACTION:
        print INVALID_COMMAND
        continue

    if clientRequestJson["Action"] == NO_MESSAGE_TO_SEND:
        print NO_MESSGAE_TO_SEND_REPLY
        continue

    clientRequestString = json.dumps(CLIENT_MESSAGE)

    clientSocket.send(clientRequestString)

    if clientRequestJson["Action"] == LOGOUT:
        sys.exit()

sys.exit()