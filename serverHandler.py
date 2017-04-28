import sys, json, time, logging
from threading import *
from serverProtocal import *
from user import *
from globalVariable import *


userList = []
fakeUser = User("NoSuchUser")

def processClientRequest(clientMessage, sock, blockDuration):
    clientAction = clientMessage["Action"]

    if clientAction == LOGIN:
        logging.debug("log in process start")
        processLogin(clientMessage, sock, blockDuration)
        return LOGIN_REPLY_MESSAGE

    if clientAction == LOGOUT:
        processLogout(clientMessage)
        return LOGOUT_REPLY_MESSAGE

    if clientAction == WHOELSE:
        processWhoelse(clientMessage)
        return WHOELSE_REPLY_MESSAGE

    if clientAction == WHOELSESINCE:
        processWhoelseSince(clientMessage)
        return WHOELSE_REPLY_MESSAGE

    if clientAction == BROADCAST:
        return BROADCAST_REPLY_MESSAGE

    if clientAction == MESSAGE:
        processMessage(clientMessage)
        return MESSAGE_REPLY_TO_SENDER

    if clientAction == BLOCK:
        processBlock(clientMessage)
        return BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE

    if clientAction == UNBLOCK:
        processUnblock(clientMessage)
        return BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE

def processLogin(clientMessage, sock, blockDuration):
    requestUsername = getRequestUsername(clientMessage)
    requestUser = getUserFromUsername(requestUsername)
    LOGIN_REPLY_MESSAGE["Username"] = requestUsername
    replyMessage = ""

    requestUserAttemptTime = requestUser.getAttemptTime()

    if requestUserAttemptTime > 2:
        LOGIN_REPLY_MESSAGE["DisplayMessage"] = LOGIN_USER_BLOCKED_MESSAGE
        LOGIN_REPLY_MESSAGE["KeepConnect"] = False
        LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
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
            replyMessage = LOGIN_WELCOME_MESSAGE

        elif loginStatus == LOGIN_INVALID_PASSWORD:
            if requestUserAttemptTime == 2:
                replyMessage = LOGIN_BLOCK_USER_MESSAGE
                LOGIN_REPLY_MESSAGE["KeepConnect"] = False
                LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
                requestUser.increaseAttemptTime()
                blockUser(requestUser, blockDuration)
            else:
                LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
                replyMessage = LOGIN_INVALID_PASSWORD_MESSAGE

        elif loginStatus == LOGIN_USER_ALREADY_LOGGEDIN:
            LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
            LOGIN_REPLY_MESSAGE["KeepConnect"] = False
            replyMessage = LOGIN_USER_ALREADY_LOGGEDIN_MESSAGE

    LOGIN_REPLY_MESSAGE["LoginStatus"] = loginStatus
    LOGIN_REPLY_MESSAGE["DisplayMessage"] = replyMessage

def login(clientInputUsername, clientInputPassword, sock):
    isUserFind = False
    loginStatus = None
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

def processLogout(clientMessage):
    username = getRequestUsername(clientMessage)
    user = getUserFromUsername(username)
    user.setUserStatus(False)
    user.setLastOnlineTime()
    user.setClientSocket(None)
    LOGOUT_REPLY_MESSAGE["Username"] = username
    LOGIN_REPLY_MESSAGE["LoginSuccess"] = False
    LOGOUT_REPLY_MESSAGE["KeepConnect"] = False
    LOGOUT_REPLY_MESSAGE["DisplayMessage"] = LOGOUT_MESSAGE
    print username, "logged out"

def processWhoelse(clientMessage):
    username = getRequestUsername(clientMessage)
    onlineUserNames = getOnlineUsername()
    onlineUserNames.remove(username)
    onlineUserNamesString = convertListToString(onlineUserNames)
    WHOELSE_REPLY_MESSAGE["DisplayMessage"] = onlineUserNamesString

def processWhoelseSince(clientMessage):
    username = getRequestUsername(clientMessage)
    timeSince = clientMessage["WhoelseSinceTime"]

    # include all online users first
    onlineUserNames = getOnlineUsername()
    onlineUserNames.remove(username)

    whoelseSince = onlineUserNames

    # then analyze offline users
    offlineUsers = getOfflineUser()
    for offlineUser in offlineUsers:
        lastOnlineTime = offlineUser.getLastOnlineTime()
        currentTime = time.time()
        timeInterval = int(currentTime - lastOnlineTime)

        if timeInterval < int(timeSince):
            whoelseSince.append(offlineUser.getUsername())

    whoelseSinceString = convertListToString(whoelseSince)
    WHOELSE_REPLY_MESSAGE["DisplayMessage"] = whoelseSinceString

def processMessage(clientMessage):
    username = getRequestUsername(clientMessage)
    sender = getUserFromUsername(username)
    receiverName = clientMessage["ReceiverName"]
    receiver = getUserFromUsername(receiverName)

    beBlockedByUsers = sender.getBeBlockedByUserList()

    if receiver.getUsername() == "NoSuchUser":
        MESSAGE_REPLY_TO_SENDER["MessageSendSuccess"] = False
        MESSAGE_REPLY_TO_SENDER["DisplayMessage"] = INVALID_USER_MESSAGE
    elif receiver.getUsername() == username:
        MESSAGE_REPLY_TO_SENDER["MessageSendSuccess"] = False
        MESSAGE_REPLY_TO_SENDER["DisplayMessage"] = MESSAGE_SEND_TO_SELF_MESSAGE
    elif receiver in beBlockedByUsers:
        MESSAGE_REPLY_TO_SENDER["MessageSendSuccess"] = False
        MESSAGE_REPLY_TO_SENDER["DisplayMessage"] = MESSAGE_BE_BLOCKED_MESSAGE
    else:
        MESSAGE_REPLY_TO_SENDER["MessageSendSuccess"] = True
        print username + " sending to " + receiverName

def processBlock(clientMessage):
    usernameToBlock = clientMessage["BlockOrUnblockUserName"]
    requestUsername = getRequestUsername(clientMessage)
    requestUser = getUserFromUsername(requestUsername)
    userToBlock = getUserFromUsername(usernameToBlock)

    if usernameToBlock == requestUsername:
        BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE["DisplayMessage"] = BLOCK_SELF_MESSAGE
    elif userToBlock.getUsername() == "NoSuchUser":
        BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE["DisplayMessage"] = INVALID_USER_MESSAGE
    else:
        userToBlock.setBeBlockedByUser(requestUser)
        requestUser.setBlockUser(userToBlock)
        BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE["DisplayMessage"] = usernameToBlock + " is blocked"

def processUnblock(clientMessage):
    usernameToUnblock = clientMessage["BlockOrUnblockUserName"]
    requestUsername = getRequestUsername(clientMessage)
    requestUser = getUserFromUsername(requestUsername)
    userToUnblock = getUserFromUsername(usernameToUnblock)

    if usernameToUnblock == requestUsername:
        BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE["DisplayMessage"] = BLOCK_SELF_MESSAGE
    elif usernameToUnblock == "NoSuchUser":
        BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE["DisplayMessage"] = INVALID_USER_MESSAGE
    else:
        try:
            userToUnblock.setBeUnblockedByUser(requestUser)
            requestUser.setUnblockUser(userToUnblock)
            BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE["DisplayMessage"] = usernameToUnblock + " is unblocked"
        except:
            BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE["DisplayMessage"] = "Error. " + usernameToUnblock + " was not blocked"

##################################################################################
## Useful methods
##################################################################################

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
    return userList

def getUserFromUsername(username):
    for user in userList:
        currentUsername = user.getUsername()
        if currentUsername == username:
            return user
    return fakeUser

def getUserFromSocket(sock):
    for user in userList:
        userSocket = user.getClientSocket()
        if userSocket == sock:
            return user
    return None

def getRequestUsername(clientMessage):
    username = clientMessage["Username"]
    return username

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

def getOnlineUserExceptCurrentSocket(currentUser):
    onlineUserExceptCurrentSockets = getOnlineUserSocket()
    currentUserSocket = currentUser.getClientSocket()
    try:
        onlineUserExceptCurrentSockets.remove(currentUserSocket)
    except:
        pass
    return onlineUserExceptCurrentSockets

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
