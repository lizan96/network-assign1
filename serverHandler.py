import sys, json, time, logging
from threading import *
from serverProtocal import *
from user import *
from globalVariable import *


userList = []

fakeUser = User("NosuchUser")

def processClientRequest(clientMessage, sock, blockDuration, timeout):
    clientAction = clientMessage["Action"]

    if clientAction == LOGIN:
        logging.debug("log in process start")
        processLogin(clientMessage, sock, blockDuration, timeout)
        return LOGIN_REPLY_MESSAGE
    if clientAction == LOGOUT:
        username = getRequestUsername(clientMessage)
        processLogout(username)
        return LOGOUT_REPLY_MESSAGE
    if clientAction == WHOELSE:
        username = getRequestUsername(clientMessage)
        onlineUserNames = processWhoelse(username)
        WHOELSE_REPLY_MESSAGE["DisplayMessage"] = onlineUserNames
        return WHOELSE_REPLY_MESSAGE
    if clientAction == WHOELSESINCE:
        username = getRequestUsername(clientMessage)
        timeSince = clientMessage["WhoelseSinceTime"]
        onlineUserNamesSinceTime = processWhoelseSince(username, timeSince)
        WHOELSE_REPLY_MESSAGE["DisplayMessage"] = onlineUserNamesSinceTime
        return WHOELSE_REPLY_MESSAGE


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

def processLogin(clientMessage, sock, blockDuration, timeout):
    requestUsername = getRequestUsername(clientMessage)
    requestUser = getUserFromUsername(requestUsername)
    LOGIN_REPLY_MESSAGE["Username"] = requestUsername

    requestUserAttemptTime = requestUser.getAttemptTime()
    # block account username

    if requestUserAttemptTime > 2:
        LOGIN_REPLY_MESSAGE["DisplayMessage"] = "Your account is blocked due to multiple login failures. Please try again later"
        LOGIN_REPLY_MESSAGE["KeepConnect"] = False
        return LOGIN_REPLY_MESSAGE

    else:
        LOGIN_REPLY_MESSAGE["KeepConnect"] = True

        loginStatus = login(requestUsername, clientMessage["Password"], sock)

        if loginStatus == LOGIN_NO_SUCH_USER:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
            replyMessage = "No such user exist"

        elif loginStatus == LOGIN_SUCCESS:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = True
            print requestUsername, "logged in"
            replyMessage = "Welcome to the greatest messaging application ever"

        elif loginStatus == LOGIN_INVALID_PASSWORD:
            if requestUserAttemptTime == 2:
                LOGIN_REPLY_MESSAGE["DisplayMessage"] = "Invalid Password. Your account has been blocked. Please try again later"
                LOGIN_REPLY_MESSAGE["KeepConnect"] = False
                requestUser.increaseAttemptTime()
                blockUser(requestUser, blockDuration)
            else:
                LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
                replyMessage = "Invalid Password. Please try again"

        elif loginStatus == LOGIN_USER_ALREADY_LOGGEDIN:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
            LOGIN_REPLY_MESSAGE["KeepConnect"] = False
            replyMessage = "User has already logged in"

    LOGIN_REPLY_MESSAGE["LoginStatus"] = loginStatus
    LOGIN_REPLY_MESSAGE["DisplayMessage"] = replyMessage

def login(clientInputUsername, clientInputPassword, sock):
    isUserFind = False
    for user in userList:
        currentUsername = user.getUsername()
        currentPassword = user.getPassword()
        if currentUsername == clientInputUsername and currentPassword == clientInputPassword:
            # if user has already logged in
            if user.isUserOnline() == True:
                loginStatus = LOGIN_USER_ALREADY_LOGGEDIN
            else:
                loginStatus = LOGIN_SUCCESS
                user.resetAttemptTime()
                user.online = True
                user.setClientSocket(sock)
            isUserFind = True
            break
        if currentUsername == clientInputUsername and currentPassword != clientInputPassword:
            if user.isUserOnline() == True:
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
    user.setUserStatus(False)
    user.setLastOnlineTime()
    user.setClientSocket(None)
    LOGOUT_REPLY_MESSAGE["Username"] = username
    LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
    LOGOUT_REPLY_MESSAGE["KeepConnect"] = False
    LOGOUT_REPLY_MESSAGE["DisplayMessage"] = "SEE YOU. BYE!!"
    print username, "logged out"

def processWhoelse(username):
    onlineUserNames = getOnlineUsername()
    onlineUserNames.remove(username)
    onlineUserNamesString = convertListToString(onlineUserNames)
    return onlineUserNamesString

def processWhoelseSince(username, timeSince):
    onlineUserNames = getOnlineUsername()
    onlineUserNames.remove(username)

    whoelseSince = onlineUserNames

    offlineUsers = getOfflineUser()
    for offlineUser in offlineUsers:
        lastOnlineTime = offlineUser.getLastOnlineTime()
        currentTime = time.time()
        timeInterval = int(currentTime - lastOnlineTime)

        if timeInterval < int(timeSince):
            whoelseSince.append(offlineUser.getUsername())

    whoelseSinceString = convertListToString(whoelseSince)
    return whoelseSinceString

def getOnlineUser():
    onlineUserList = []
    for user in userList:
        if user.isUserOnline():
            onlineUserList.append(user)
    return onlineUserList

def getOnlineUserSocket():
    onlineUserSocketList = []
    for user in userList:
        if user.isUserOnline():
            onlineUserSocketList.append(user.getClientSocket())
    return onlineUserSocketList

def getOnlineUsername():
    onlineUsernameList = []
    for user in userList:
        if user.isUserOnline():
            onlineUsernameList.append(user.getUsername())
    return onlineUsernameList

def getOfflineUser():
    onlineUserList = []
    for user in userList:
        if not user.isUserOnline():
            onlineUserList.append(user)
    return onlineUserList

def convertListToString(userNamelist):
    if len(userNamelist) == 0:
        return ""
    userNamelistString = userNamelist[0]
    for username in userNamelist[1:]:
        userNamelistString = userNamelistString + "\n" + username
    return userNamelistString

def resetUserAttemptTime(user):
    user.resetAttemptTime()

def blockUser(user, blockDuration):
    t = Timer(blockDuration, user.resetAttemptTime)
    t.start()
