import sys, json, time, logging
from socket import *
from thread import *
from select import *
from serverProtocal import *
import serverHandler
from globalVariable import *

serverPort = int(sys.argv[1])
blockDuration = int(sys.argv[2])
timeout = int(sys.argv[3])

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)

print "Server started"

# create user list according to credentials.txt when server starts
serverHandler.createUserList()

def disconnectSocket(rlistList, wlistList, addresses, sock):
    del addresses[sock]
    try:
        rlistList.remove(sock)
        wlistList.remove(sock)
    except:
        pass
    sock.close()
    return (rlistList, wlistList, addresses)

def addMessageToSendList(jsonMessage, sock, wlistList, data):
    jsonMessageToString = json.dumps(jsonMessage)
    data[sock] = data.get(sock, '') + jsonMessageToString
    if sock not in wlistList:
        wlistList.append(sock)
    return wlistList, data

# receive from clients
rlistList = [serverSocket]
# send to clients
wlistList = []
# mapping socket to data to be sent
data = {}
# mapping socket to (host, port)
addresses = {}

try:
    # server always on
    while True:
        rlist, wlist, xlist = select(rlistList, wlistList, [])
        for sock in rlist:
            if sock is serverSocket:
                # client trying to connect
                newSocket, address = serverSocket.accept()
                print "Connected from", address[0], ":", address[1]
                rlistList.append(newSocket)
                addresses[newSocket] = address
            else:
                # other events
                clientMessage = sock.recv(1024).decode('utf-8')
                if clientMessage:
                    clientMessageJson = json.loads(clientMessage)
                    replyMessageJson = serverHandler.processClientRequest(clientMessageJson, sock, blockDuration, timeout)

                    if clientMessageJson["Action"] == LOGOUT:
                        logoutUsername = replyMessageJson["Username"]
                        logoutUser = serverHandler.getUserFromUsername(logoutUsername)
                        LOGOUT_TO_OTHER_USER["DisplayMessage"] = logoutUsername + " logged out"
                        messageToOtherUserJson = LOGOUT_TO_OTHER_USER
                        replyMessageString = json.dumps(replyMessageJson)

                        sock.send(replyMessageString)
                        rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)

                        onlineUserSockets = serverHandler.getOnlineUserSocket()

                        blockedUserSockets = logoutUser.getBlockedUserSocket()

                        for onlineUserSocket in onlineUserSockets:
                            if onlineUserSocket in blockedUserSockets:
                                continue
                            wlistList, data = addMessageToSendList(messageToOtherUserJson, onlineUserSocket, wlistList, data)

                    elif (clientMessageJson["Action"] == LOGIN and replyMessageJson["LoginStatus"] == LOGIN_SUCCESS):
                        loginUsername = replyMessageJson["Username"]
                        loginUser = serverHandler.getUserFromUsername(loginUsername)

                        LOGIN_TO_OTHER_USER["DisplayMessage"] = loginUsername + " logged in"

                        messageToOtherUserJson = LOGIN_TO_OTHER_USER

                        replyMessageString = json.dumps(replyMessageJson)
                        data[sock] = data.get(sock, '') + replyMessageString

                        offlineMessage = loginUser.getOfflineMessageInString()
                        if offlineMessage:
                            print "have offline message"
                            MESSAGE_TO_RECEIVER["DisplayMessage"] = offlineMessage
                            messageToReceiverString = json.dumps(MESSAGE_TO_RECEIVER)
                            data[sock] = data.get(sock, '') + "/" + messageToReceiverString
                            print messageToReceiverString

                        if sock not in wlistList:
                            wlistList.append(sock)

                        onlineUserSockets = serverHandler.getOnlineUserExceptCurrentSocket(loginUser)
                        blockedUserSockets = loginUser.getBlockedUserSocket()

                        for onlineUserSocket in onlineUserSockets:
                            if onlineUserSocket in blockedUserSockets:
                                continue
                            wlistList, data = addMessageToSendList(messageToOtherUserJson, onlineUserSocket,
                                                                       wlistList, data)

                    elif clientMessageJson["Action"] == LOGIN:
                        if replyMessageJson["KeepConnect"] == False:
                            replyMessageString = json.dumps(replyMessageJson)
                            insent = sock.send(replyMessageString)
                            print "logout: disconnected", addresses[sock]
                            rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)

                    elif clientMessageJson["Action"] == BROADCAST:
                        requestUsername = clientMessageJson["Username"]
                        requestUser = serverHandler.getUserFromUsername(requestUsername)
                        print requestUsername + " broadcasting"

                        displayMessage = clientMessageJson["Username"] + ": " + clientMessageJson["BroadcastMessage"]
                        BROADCAST_TO_OTHER_USER["DisplayMessage"] = displayMessage

                        onlineUserSockets = serverHandler.getOnlineUserExceptCurrentSocket(requestUser)

                        beBlockedByUserSockets = requestUser.getBeBlockedByUserSocket()

                        for onlineUserSocket in onlineUserSockets:
                            if onlineUserSocket in beBlockedByUserSockets:
                                replyMessageJson["DisplayMessage"] = BROADCAST_FAILED_TO_SOME_USER
                                wlistList, data = addMessageToSendList(replyMessageJson, sock, wlistList, data)
                                continue
                            wlistList, data = addMessageToSendList(BROADCAST_TO_OTHER_USER, onlineUserSocket, wlistList, data)

                    elif clientMessageJson["Action"] == MESSAGE:
                        if replyMessageJson["MessageSendSuccess"] == False:
                            wlistList, data = addMessageToSendList(replyMessageJson, sock, wlistList, data)
                        else:
                            receiverName = clientMessageJson["ReceiverName"]
                            message = clientMessageJson["Message"]
                            displayMessage = clientMessageJson["Username"] + ": " + message
                            receiver = serverHandler.getUserFromUsername(receiverName)
                            receiverSocket = receiver.getClientSocket()

                            if receiverSocket:
                                MESSAGE_TO_RECEIVER["DisplayMessage"] = displayMessage
                                wlistList, data = addMessageToSendList(MESSAGE_TO_RECEIVER, receiverSocket, wlistList, data)
                            else:
                                receiver.addOfflineMessage(displayMessage)
                    else:
                        wlistList, data = addMessageToSendList(replyMessageJson, sock, wlistList, data)

        for sock in wlist:
            tosend = data.get(sock)
            if tosend:
                nsent = sock.send(tosend)
                # remember data still to be sent, if any
                tosend = tosend[nsent:]
            if tosend:
                data[sock] = tosend
            else:
                try:
                    del data[sock]
                except KeyError:
                    pass
                wlistList.remove(sock)
finally:
    serverSocket.close()