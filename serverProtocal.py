import json
from globalVariable import *


LOGIN_BLOCK_USER_MESSAGE = "Invalid Password. Your account has been blocked. Please try again later"
LOGIN_USER_BLOCKED_MESSAGE = "Your account is blocked due to multiple login failures. Please try again later"
LOGIN_WELCOME_MESSAGE = "Welcome to the greatest messaging application ever"
LOGIN_INVALID_PASSWORD_MESSAGE = "Invalid Password. Please try again"
LOGIN_USER_ALREADY_LOGGEDIN_MESSAGE = "User has already logged in"

LOGOUT_TO_OTHER_MESSAGE = "{} logged out"

BROADCAST_FAILED_TO_SOME_USER = "Your message could not be delivered to some recipients"

INVALID_USER_MESSAGE = "Error. No such user"

MESSAGE_SEND_TO_SELF_MESSAGE = "Error. You cannot send message to yourself"
MESSAGE_BE_BLOCKED_MESSAGE = "Your message could not be delivered as the recipient has blocked you"

BLOCK_SELF_MESSAGE = "Error. Cannot block/unblock self"

LOGIN_REPLY_MESSAGE = {
    "KeepConnect": True,
    "Username": "",
    "LoginSuccess": False,
    "DisplayMessage": "",
    "LoginStatus": LOGIN_NO_SUCH_USER
}

LOGOUT_REPLY_MESSAGE = {
    "KeepConnect": False,
    "Username": "",
    "DisplayMessage": ""
}

LOGOUT_TO_OTHER_USER = {
    "DisplayMessage": LOGOUT_TO_OTHER_MESSAGE,
    "KeepConnect": True
}

LOGIN_TO_OTHER_USER = {
    "DisplayMessage": "",
    "KeepConnect": True
}

WHOELSE_REPLY_MESSAGE = {
    "KeepConnect": True,
    "DisplayMessage": ""
}

BROADCAST_REPLY_MESSAGE = {
    "KeepConnect": True,
    "DisplayMessage": ""
}

BROADCAST_TO_OTHER_USER = {
    "BroadcastFromUsername": "",
    "DisplayMessage": "",
    "KeepConnect": True
}

MESSAGE_TO_RECEIVER = {
    "DisplayMessage": "",
    "KeepConnect": True
}

MESSAGE_REPLY_TO_SENDER = {
    "BroadcastFromUsername": "",
    "DisplayMessage": "",
    "KeepConnect": True,
    "MessageSendSuccess": True
}

BLOCK_OR_UNBLOCK_USER_REPLY_MESSAGE = {
    "KeepConnect": True,
    "DisplayMessage": ""
}