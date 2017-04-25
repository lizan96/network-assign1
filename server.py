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
                    replyMessageJson = serverHandler.processClientRequest(clientMessageJson, blockDuration, timeout)
                    if clientMessageJson["Action"] == LOGOUT:
                        replyMessageString = json.dumps(replyMessageJson)
                        print replyMessageString
                        insent = sock.send(replyMessageString)
                        print "logout: disconnected", addresses[sock][1]
                        rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)
                    elif (clientMessageJson["Action"] == LOGIN and replyMessageJson["KeepConnect"] == False) or replyMessageJson["DisplayMessage"] == LOGIN_USER_ALREADY_LOGGEDIN:
                        replyMessageString = json.dumps(replyMessageJson)
                        insent = sock.send(replyMessageString)
                        print "logout: disconnected", addresses[sock]
                        # del addresses[sock]
                        # try:
                        #     rlistList.remove(sock)
                        #     wlistList.remove(sock)
                        # except:
                        #     pass
                        # sock.close()
                        rlistList, wlistList, addresses = disconnectSocket(rlistList, wlistList, addresses, sock)
                    else:
                        replyMessageString = json.dumps(replyMessageJson)
                        print replyMessageString
                        data[sock] = data.get(sock, '') + replyMessageString
                        if sock not in wlistList:
                            wlistList.append(sock)

        for sock in wlist:
            # output events always mean we can send some data
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
                print "No data currently remain for", addresses[sock]

finally:
    serverSocket.close()