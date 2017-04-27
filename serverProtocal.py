import json
from globalVariable import *

LOGOUT_TO_OTHER_MESSAGE = "{} logged out"

LOGIN_REPLY_MESSAGE = {
    "KeepConnect": True,
    "Username": "",
    "LoginSuccess": False,
    "DisplayMessage": "",
    "BlockDuration": 0,
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

GENERAL_REPLY_MESSAGE = {
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