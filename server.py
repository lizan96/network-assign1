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

print "The server is ready to receive"
serverHandler.createUserList()

def closeSocket(sock, rlistList, wlistList, addr):
    del addr[sock]
    try:
        rlistList.remove(sock)
        wlistList.remove(sock)
    except:
        pass
    sock.close()


# lists of sockets to watch for input and output events
rlistList = [serverSocket]
wlistList = []
# mapping socket -> data to send on that socket when feasible
data = {}
# mapping socket -> (host, port) on which the client is running
addresses = {}

def disconnectSocket(rlistList, wlistList, addresses, sock):
    del addresses[sock]
    try:
        rlistList.remove(sock)
        wlistList.remove(sock)
    except:
        pass
    sock.close()

    return (rlistList, wlistList, addresses)
try:
    while True:
        rlist, wlist, xlist = select(rlistList, wlistList, [])
        for sock in rlist:
            if sock is serverSocket:
                # input event on sock means client trying to connect
                newSocket, address = serverSocket.accept()
                print "Connected from", address[0], ":", address[1]
                rlistList.append(newSocket)
                addresses[newSocket] = address
            else:
                # other input events mean data arrived, or disconnections
                clientMessage = sock.recv(1024).decode('utf-8')
                if clientMessage:
                    clientMessageJson = json.loads(clientMessage)
                    replyMessageJson = serverHandler.processClientRequest(clientMessageJson, sock, blockDuration, timeout)

                    if clientMessageJson["Action"] == LOGOUT:
                        logoutUsername = replyMessageJson["Username"]
                        LOGOUT_TO_OTHER_USER["DisplayMessage"] = logoutUsername + " logged out"
                        messageToOtheruserJson = LOGOUT_TO_OTHER_USER
                        messageToOtheruserString = json.dumps(messageToOtheruserJson)

                        replyMessageString = json.dumps(replyMessageJson)

                        sock.send(replyMessageString)
                        rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)

                        onlineUserSockets = serverHandler.getOnlineUserSocket()
                        print onlineUserSockets

                        for onlineUserSocket in onlineUserSockets:
                            data[onlineUserSocket] = data.get(onlineUserSocket, '') + messageToOtheruserString
                            if onlineUserSocket not in wlistList:
                                wlistList.append(onlineUserSocket)

                    elif (clientMessageJson["Action"] == LOGIN and replyMessageJson["LoginStatus"] == LOGIN_SUCCESS):
                        loginUsername = replyMessageJson["Username"]
                        LOGIN_TO_OTHER_USER["DisplayMessage"] = loginUsername + " logged in"

                        messageToOtheruserJson = LOGIN_TO_OTHER_USER
                        messageToOtheruserString = json.dumps(messageToOtheruserJson)

                        replyMessageString = json.dumps(replyMessageJson)
                        data[sock] = data.get(sock, '') + replyMessageString
                        if sock not in wlistList:
                            wlistList.append(sock)

                        onlineUserSockets = serverHandler.getOnlineUserSocket()
                        onlineUserSockets.remove(sock)

                        for onlineUserSocket in onlineUserSockets:
                            data[onlineUserSocket] = data.get(onlineUserSocket, '') + messageToOtheruserString
                            if onlineUserSocket not in wlistList:
                                wlistList.append(onlineUserSocket)

                    elif (clientMessageJson["Action"] == LOGIN and replyMessageJson["KeepConnect"] == False) or replyMessageJson["DisplayMessage"] == LOGIN_USER_ALREADY_LOGGEDIN:
                        replyMessageString = json.dumps(replyMessageJson)
                        insent = sock.send(replyMessageString)
                        print "logout: disconnected", addresses[sock]
                        rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)

                    elif clientMessageJson["Action"] == BROADCAST:
                        print clientMessageJson["Username"], "broadcasting"
                        displayMessage = clientMessageJson["Username"] + ": " + clientMessageJson["BroadcastMessage"]
                        BROADCAST_TO_OTHER_USER["DisplayMessage"] = displayMessage
                        broadcastToOtherUserString = json.dumps(BROADCAST_TO_OTHER_USER)

                        onlineUserSockets = serverHandler.getOnlineUserSocket()
                        onlineUserSockets.remove(sock)

                        for onlineUserSocket in onlineUserSockets:
                            data[onlineUserSocket] = data.get(onlineUserSocket, '') + broadcastToOtherUserString
                            if onlineUserSocket not in wlistList:
                                wlistList.append(onlineUserSocket)

                    else:
                        replyMessageString = json.dumps(replyMessageJson)
                        # print replyMessageString
                        data[sock] = data.get(sock, '') + replyMessageString
                        if sock not in wlistList:
                            wlistList.append(sock)

        for sock in wlist:
            # output events always mean we can send some data
            tosend = data.get(sock)
            if tosend:
                nsent = sock.send(tosend)
                # remember data still to be sent, if any
                print nsent, sock
                tosend = tosend[nsent:]

            if tosend:
                data[sock] = tosend
            else:
                try:
                    del data[sock]
                except KeyError:
                    pass
                wlistList.remove(sock)
                print "No data currently remain for", addresses[sock]

finally:
    serverSocket.close()