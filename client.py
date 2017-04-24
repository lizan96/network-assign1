import logging, sys, json
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
isLoginSuccess = True

username = raw_input('Username: ')
password = raw_input('Password: ')
CLIENT_MESSAGE["Action"] = LOGIN
CLIENT_MESSAGE["Username"] = username
CLIENT_MESSAGE["Password"] = password

clientRequest = json.dumps(CLIENT_MESSAGE)
print clientRequest
clientSocket.send(clientRequest)

receivedMessage = clientSocket.recv(1024)
receivedMessageJson = json.loads(receivedMessage)
desplayMessage = receivedMessageJson["DisplayMessage"]
isLoginSuccess = receivedMessageJson["LoginSuccess"]
keepConnect = receivedMessageJson["KeepConnect"]
print desplayMessage

while keepConnect and not isLoginSuccess:
    password = raw_input('Password: ')
    CLIENT_MESSAGE["Password"] = password

    clientRequest = json.dumps(CLIENT_MESSAGE)
    print clientRequest
    clientSocket.send(clientRequest)

    receivedMessage = clientSocket.recv(1024)
    receivedMessageJson = json.loads(receivedMessage)
    desplayMessage = receivedMessageJson["DisplayMessage"]
    isLoginSuccess = receivedMessageJson["LoginSuccess"]
    keepConnect = receivedMessageJson["KeepConnect"]
    print desplayMessage

while isLoginSuccess:
    clientRequest = raw_input()
    clientRequestJson = parseClientRequest(clientRequest)
    clientRequestString = json.dumps(CLIENT_MESSAGE)
    logging.debug(clientRequestString)
    clientSocket.send(clientRequestString)
    if clientRequest == "logout":
        sys.exit()
    receivedMessage = clientSocket.recv(1024)