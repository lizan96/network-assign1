import json

LOGIN_NO_SUCH_USER = 0
LOGIN_SUCCESS = 1
LOGIN_INVALID_PASSWORD = 2
LOGIN_USER_BLOCKED = 3

LOGIN_REPLY_MESSAGE = {
    "KeepConnect": True,
    "Username": "",
    "LoginSuccess": False,
    "DisplayMessage": "",
    "BlockDuration": 0,
    "LoginStatus": LOGIN_NO_SUCH_USER
}
