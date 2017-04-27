import json
from globalVariable import *

LOGOUT_TO_OTHER_MESSAGE = "{} logged out"
BROADCAST_FAILED_TO_SOME_USER = "Your message could not be delivered to some recipients"

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