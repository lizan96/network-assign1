import sys, json, time, logging
from threading import *
from serverProtocal import *
from user import *
from globalVariable import *


userList = []

fakeUser = User("NosuchUser")

def processClientRequest(clientMessage, blockDuration, timeout):
    clientAction = clientMessage["Action"]

    if clientAction == LOGIN:
        logging.debug("log in process start")
        replyMessage = processLogin(clientMessage, blockDuration, timeout)
        return replyMessage
    if clientAction == LOGOUT:
        username = getRequestUsername(clientMessage)
        replyMessage = processLogout(username)
        return replyMessage

def createUserObject(clientInputUsername):
    User(clientInputUsername)

def createUserList():
    f = open("credentials.txt", "r")
    for line in f:
        credential = line.split()
        username = credential[0]
        password = credential[1]
        newUser = User(username)
        newUser.setPassword(password)
        userList.append(newUser)

def getUserFromUsername(username):
    for user in userList:
        currentUsername = user.getUsername()
        if currentUsername == username:
            return user
    return fakeUser

def getRequestUsername(clientMessage):
    username = clientMessage["Username"]
    return username

def processLogin(clientMessage, blockDuration, timeout):
    requestUsername = getRequestUsername(clientMessage)
    requestUser = getUserFromUsername(requestUsername)

    requestUserAttemptTime = requestUser.getAttemptTime()
    # block account username
    if requestUserAttemptTime == 2:
        LOGIN_REPLY_MESSAGE["DisplayMessage"] = "Invalid Password. Your account has been blocked. Please try again later"
        LOGIN_REPLY_MESSAGE["KeepConnect"] = False
        requestUser.increaseAttemptTime()
        blockUser(requestUser, blockDuration)
        return LOGIN_REPLY_MESSAGE

    elif requestUserAttemptTime > 2:
        LOGIN_REPLY_MESSAGE["DisplayMessage"] = "Your account is blocked due to multiple login failures. Please try again later"
        LOGIN_REPLY_MESSAGE["KeepConnect"] = False
        return LOGIN_REPLY_MESSAGE

    else:
        LOGIN_REPLY_MESSAGE["KeepConnect"] = True

        loginStatus = login(requestUsername, clientMessage["Password"])

        if loginStatus == LOGIN_NO_SUCH_USER:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
            replyMessage = "No such user exist"

        elif loginStatus == LOGIN_SUCCESS:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = True
            print requestUsername, "logged in"
            replyMessage = "Welcome to the greatest messaging application ever"

        elif loginStatus == LOGIN_INVALID_PASSWORD:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
            replyMessage = "Invalid Password. Please try again"

        elif loginStatus == LOGIN_USER_ALREADY_LOGGEDIN:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
            LOGIN_REPLY_MESSAGE["KeepConnect"] = False
            replyMessage = "User has already logged in"

    LOGIN_REPLY_MESSAGE["LoginStatus"] = loginStatus
    LOGIN_REPLY_MESSAGE["DisplayMessage"] = replyMessage
    return LOGIN_REPLY_MESSAGE

def login(clientInputUsername, clientInputPassword):
    isUserFind = False
    for user in userList:
        currentUsername = user.getUsername()
        currentPassword = user.getPassword()
        if currentUsername == clientInputUsername and currentPassword == clientInputPassword:
            # if user has already logged in
            if user.getUserStatus() == True:
                loginStatus = LOGIN_USER_ALREADY_LOGGEDIN
            else:
                loginStatus = LOGIN_SUCCESS
                user.setLogInTime()
                user.resetAttemptTime()
                user.online = True
            isUserFind = True
            break
        if currentUsername == clientInputUsername and currentPassword != clientInputPassword:
            if user.getUserStatus() == True:
                loginStatus = LOGIN_USER_ALREADY_LOGGEDIN
            else:
                loginStatus = LOGIN_INVALID_PASSWORD
                user.increaseAttemptTime()
            isUserFind = True
            break

    if not isUserFind:
        loginStatus = LOGIN_NO_SUCH_USER
        fakeUser.increaseAttemptTime()
    return loginStatus

def processLogout(username):
    user = getUserFromUsername(username)
    user.setUserStatue(False)
    LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
    LOGIN_REPLY_MESSAGE["KeepConnect"] = False
    return LOGIN_REPLY_MESSAGE

def resetUserAttemptTime(user):
    user.resetAttemptTime()

def blockUser(user, blockDuration):
    t = Timer(blockDuration, user.resetAttemptTime)
    t.start()
