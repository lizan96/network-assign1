import logging, sys, json, random


class User:
    def __init__(self, username):
        self.username = username
        self.blockTime = 0
        self.attemptTime = 0
        self.online = False

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
    def setUserStatue(self, status):
        self.online = status

    def getUserStatus(self):
        return self.online
