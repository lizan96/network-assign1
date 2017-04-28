import logging, sys, json, random, time


class User:
    def __init__(self, username):
        self.username = username
        self.blockTime = 0
        self.attemptTime = 0
        self.online = False
        self.sock = None
        self.blockUserList = []
        self.beBlockedByUserList = []
        self.offLineMessage = []
        self.lastOnlineTime = 0
        self.lastCommandSentTime = 0
        self.isTimeout = False

    ##################################################################################
    def getUsername(self):
        return self.username

    ##################################################################################
    ## password
    ##################################################################################
    def setPassword(self, password):
        self.password = password

    def getPassword(self):
        return self.password

    ##################################################################################
    ## client socket
    ##################################################################################
    def setClientSocket(self, sock):
        self.sock = sock

    def getClientSocket(self):
        return self.sock

    ##################################################################################
    ## attempt time
    ##################################################################################
    def increaseAttemptTime(self):
        self.attemptTime += 1

    def resetAttemptTime(self):
        self.attemptTime = 0

    def getAttemptTime(self):
        return self.attemptTime
    ##################################################################################
    ## user online status
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
    ## block/unblock
    ##################################################################################
    def setBlockUser(self, user):
        self.blockUserList.append(user)

    def setUnblockUser(self, user):
        self.blockUserList.remove(user)

    def setBeUnblockedByUser(self, user):
        self.beBlockedByUserList.remove(user)

    def setBeBlockedByUser(self, user):
        self.beBlockedByUserList.append(user)

    def getBlockUsersList(self):
        return self.blockUserList

    def getBeBlockedByUserList(self):
        return self.beBlockedByUserList

    def getBeBlockedByUserSocket(self):
        beBlockedByUserSockets = []
        for beBlockedByUser in self.beBlockedByUserList:
            beBlockedBySocket = beBlockedByUser.getClientSocket()
            beBlockedByUserSockets.append(beBlockedBySocket)
        return beBlockedByUserSockets

    def getBlockedUserSocket(self):
        blockedUserSockets = []
        for blockedUser in self.blockUserList:
            blockedUserSocket = blockedUser.getClientSocket()
            blockedUserSockets.append(blockedUserSocket)
        return blockedUserSockets

    ##################################################################################
    ## offline message
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

    ##################################################################################
    ## offline message
    ##################################################################################
    def setLastCommandSentTime(self):
        self.lastCommandSentTime = time.time()

    def getLastCommandSentTime(self):
        return self.lastCommandSentTime

    def checkTimeout(self, timeout):
        isTimeout = False
        currentTime = time.time()
        inactivePeriod = currentTime - self.lastCommandSentTime
        if inactivePeriod > timeout:
            isTimeout = True
        return isTimeout