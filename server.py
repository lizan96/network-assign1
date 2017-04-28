import sys, json, time, logging, threading
from socket import *
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

# receive from clients
rlistList = [serverSocket]
# send to clients
wlistList = []
# mapping socket to data to be sent
data = {}
# mapping socket to (host, port)
addresses = {}

# socket list without serverSocket
socketList = []

print "Server started"

# create user list according to credentials.txt when server starts
userList = serverHandler.createUserList()

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

def logoutUser(replyMessageJson, rlistList, wlistList, addresses, sock, data):
    logoutUsername = replyMessageJson["Username"]
    logoutUser = serverHandler.getUserFromUsername(logoutUsername)
    LOGOUT_TO_OTHER_USER["DisplayMessage"] = logoutUsername + " logged out"
    replyMessageString = json.dumps(replyMessageJson)

    sock.send(replyMessageString)
    rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)

    rlistList, wlistList, data = presenceNotification(LOGOUT_TO_OTHER_USER, logoutUser, rlistList, wlistList, data)
    return rlistList, wlistList, addresses, data

def presenceNotification(message, clientUser, rlistList, wlistList, data):
    onlineUserSockets = serverHandler.getOnlineUserExceptCurrentSocket(clientUser)
    blockedUserSockets = clientUser.getBlockedUserSocket()
    for onlineUserSocket in onlineUserSockets:
        if onlineUserSocket in blockedUserSockets:
            continue
        wlistList, data = addMessageToSendList(message, onlineUserSocket,  wlistList, data)
    return rlistList, wlistList, data
##################################################################################
##################################################################################
try:
    # server always on
    while True:
        try:
            for sock in socketList:
                try:
                    socketUser = serverHandler.getUserFromSocket(sock)
                    isTimeout = socketUser.checkTimeout(timeout)
                    if isTimeout:
                        socketUsername = socketUser.getUsername()
                        print serverHandler.getTimestamp() + " " + socketUsername + " timeout!"
                        AUTOMATICALLY_LOGOUT["Username"] = socketUsername
                        clientMessageJson = AUTOMATICALLY_LOGOUT
                        replyMessageJson = serverHandler.processClientRequest(clientMessageJson, sock, blockDuration)
                        AUTOMATICALLY_LOGOUT_REPLY_MESSAGE["Username"] = socketUsername
                        replyMessageJson = AUTOMATICALLY_LOGOUT_REPLY_MESSAGE
                        rlistList, wlistList, addresses, data = logoutUser(replyMessageJson, rlistList, wlistList,
                                                                           addresses, sock, data)
                        socketList.remove(sock)
                except:
                    pass

            # set timeout to be 1 second in case there is no event at all
            # so that it will not block user socket timeout checking above
            rlist, wlist, xlist = select(rlistList, wlistList, [], 1)
            for sock in rlist:
                if sock is serverSocket:
                    # client trying to connect
                    newSocket, address = serverSocket.accept()
                    print serverHandler.getTimestamp() + " Connected from", address[0], ":", address[1]
                    rlistList.append(newSocket)
                    socketList.append(newSocket)
                    addresses[newSocket] = address
                else:
                    # receiving request from clients
                    clientMessage = sock.recv(1024).decode('utf-8')
                    if clientMessage:
                        clientMessageJson = json.loads(clientMessage)

                        # send client message to severHandler to resolve
                        replyMessageJson = serverHandler.processClientRequest(clientMessageJson, sock, blockDuration)
                        clientUsername = clientMessageJson["Username"]
                        clientUser = serverHandler.getUserFromUsername(clientUsername)
                        clientUser.setLastCommandSentTime()

                        if clientMessageJson["Action"] == LOGOUT:
                            rlistList, wlistList, addresses, data = logoutUser(replyMessageJson, rlistList, wlistList, addresses, sock, data)

                        elif clientMessageJson["Action"] == LOGIN:
                            if replyMessageJson["LoginStatus"] == LOGIN_SUCCESS:
                                LOGIN_TO_OTHER_USER["DisplayMessage"] = clientUsername + " logged in"

                                replyMessageString = json.dumps(replyMessageJson)
                                data[sock] = data.get(sock, '') + replyMessageString

                                # check if any offline message and send
                                offlineMessage = clientUser.getOfflineMessageInString()
                                if offlineMessage:
                                    MESSAGE_TO_RECEIVER["DisplayMessage"] = offlineMessage
                                    messageToReceiverString = json.dumps(MESSAGE_TO_RECEIVER)
                                    data[sock] = data.get(sock, '') + "/" + messageToReceiverString
                                if sock not in wlistList:
                                    wlistList.append(sock)

                                rlistList, wlistList, data = presenceNotification(LOGIN_TO_OTHER_USER, clientUser, rlistList, wlistList, data)
                            elif replyMessageJson["KeepConnect"] == False:
                                replyMessageString = json.dumps(replyMessageJson)
                                insent = sock.send(replyMessageString)
                                rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)

                            else:
                                wlistList, data = addMessageToSendList(replyMessageJson, sock, wlistList, data)

                        elif clientMessageJson["Action"] == BROADCAST:
                            print serverHandler.getTimestamp() + " " + clientUsername + " broadcasting"
                            displayMessage = clientMessageJson["Username"] + ": " + clientMessageJson["BroadcastMessage"]
                            BROADCAST_TO_OTHER_USER["DisplayMessage"] = displayMessage

                            onlineUserSockets = serverHandler.getOnlineUserExceptCurrentSocket(clientUser)
                            beBlockedByUserSockets = clientUser.getBeBlockedByUserSocket()

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

                                # check whether receiver socket exists,
                                # if not, add to receiver's offline message list
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
                    # remember data still to be sent
                    tosend = tosend[nsent:]
                # if any data leftout to be sent
                if tosend:
                    data[sock] = tosend
                else:
                    try:
                        del data[sock]
                    except KeyError:
                        pass
                    wlistList.remove(sock)
        except:
            pass
finally:
    serverSocket.close()