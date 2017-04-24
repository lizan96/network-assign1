import sys, json, time, logging
from socket import *
from thread import *
from select import *
from serverProtocal import *
import serverHandler
from globalVariable import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

serverPort = int(sys.argv[1])
blockDuration = int(sys.argv[2])
timeout = int(sys.argv[3])

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(10)

print "The server is ready to receive"
serverHandler.createUserList()
#
# # log in first --> establish connection
# # keep connecting
# # so while loop -> no use
#
# def clientThread(conn):
#     # infinite loop so that function do not terminate and thread do not end.
#     # while 1:
#     # receive request from client
#     clientMessage = conn.recv(1024).decode('utf-8')
#     try:
#         logging.debug(json.loads(clientMessage))
#         clientMessageJson = json.loads(clientMessage)
#
#         # process request
#         replyMessage = serverHandler.processClientRequest(clientMessageJson, blockDuration, timeout)
#
#         # send reply message
#         replyMessageString = json.dumps(replyMessage)
#         logging.debug(replyMessage)
#         conn.send(replyMessageString)
#     except:
#         pass
#

# while 1:
#     connectionSocket, addr = serverSocket.accept()
#     logging.debug('Connected with ' + addr[0] + ':' + str(addr[1]))
#     start_new_thread(clientThread, (connectionSocket,))
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

try:
    while True:
        rlist, wlist, xlist = select(rlistList, wlistList, [])
        for sock in rlist:
            if sock is serverSocket:
                # input event on sock means client trying to connect
                newSocket, address = serverSocket.accept()
                # logging.debug("Connected from", address[0], ":", address[1])
                rlistList.append(newSocket)
                addresses[newSocket] = address
            else:
                # other input events mean data arrived, or disconnections
                clientMessage = sock.recv(1024).decode('utf-8')
                if clientMessage:
                    clientMessageJson = json.loads(clientMessage)
                    replyMessageJson = serverHandler.processClientRequest(clientMessageJson, blockDuration, timeout)
                    if clientMessageJson["Action"] == LOGOUT:
                        # logging.debug("logout disconnected", addresses[sock])
                        del addresses[sock]
                        try:
                            rlistList.remove(sock)
                            wlistList.remove(sock)
                        except:
                            pass
                        sock.close()
                    elif clientMessageJson["Action"] == LOGIN and replyMessageJson["KeepConnect"] == False:
                        receivedMessageString = json.dumps(replyMessageJson)
                        insent = sock.send(receivedMessageString)
                        # logging.debug("logout disconnected", addresses[sock])
                        del addresses[sock]
                        try:
                            rlistList.remove(sock)
                            wlistList.remove(sock)
                        except:
                            pass
                        sock.close()
                    else:
                        receivedMessageString = json.dumps(replyMessageJson)
                        data[sock] = data.get(sock, '') + receivedMessageString
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
                # logging.debug("%d bytes remain for %s" % (len(tosend), addresses[sock]))
                data[sock] = tosend
            else:
                try:
                    del data[sock]
                except KeyError:
                    pass
                wlistList.remove(sock)
                # logging.debug("No data currently remain for", addresses[sock])

finally:
    serverSocket.close()