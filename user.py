import logging, sys, json, random, time


class User:
    def __init__(self, username):
        self.username = username
        self.blockTime = 0
        self.attemptTime = 0
        self.online = False
        self.lastOnlineTime = 0
        self.sock = None
        self.blockUserList = []
        self.beBlockedByUserList = []
        self.offLineMessage = []

    ##################################################################################
    def getUsername(self):
        return self.username
    ##################################################################################
    ##################################################################################
    def setPassword(self, password):
        self.password = password

    def getPassword(self):
        return self.password
    ##################################################################################
    ##################################################################################
    def setClientPort(self, clientPort):
        self.clientPort = clientPort

    def getClientPort(self):
        return self.clientPort

    def setClientSocket(self, sock):
        self.sock = sock

    def getClientSocket(self):
        return self.sock
    ##################################################################################
    ##################################################################################
    def increaseAttemptTime(self):
        self.attemptTime += 1

    def resetAttemptTime(self):
        self.attemptTime = 0

    def getAttemptTime(self):
        return self.attemptTime
    ##################################################################################
    ##################################################################################
    # def getBlockTime(self):
    #     return self.blockTime
    #
    # def increaseBlockTime(self):
    #     self.blockTime += 1
    ##################################################################################
    ##################################################################################
    def setUserStatus(self, status):
        self.online = status

    def setLastOnlineTime(self):
        self.lastOnlineTime = time.time()

    def getLastOnlineTime(self):
        return self.lastOnlineTime

    def isUserOnline(self):
        return self.online
    ##################################################################################
    ##################################################################################
    def setBlockUser(self, user):
        self.blockUserList.append(user)
    def getBlockUsersList(self):
        return self.blockUserList

    def setBeBlockedByUser(self, user):
        self.beBlockedByUserList.append(user)

    def getBeBlockedByUserList(self):
        return self.beBlockedByUserList

    ##################################################################################
    ##################################################################################
    def addOfflineMessage(self, message):
        self.offLineMessage.append(message)

    def getOfflineMessageInString(self):
        allOfflineMessage = ""
        try:
            allOfflineMessage = self.offLineMessage[0]
            for message in self.offLineMessage[1:]:
                allOfflineMessage = allOfflineMessage + "\n" + message
        except:
            pass
        return allOfflineMessage