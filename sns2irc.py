import socket, ssl
from ast import literal_eval
import os

IRC_NICK = os.environ["IRC_NICK"]
IRC_HOST = os.environ["IRC_HOST"]
IRC_PORT = int(os.environ["IRC_PORT"])
IRC_SSL = literal_eval(os.environ["IRC_SSL"])
IRC_CHAN = os.environ["IRC_CHAN"]
IRC_PASS = os.environ["IRC_PASS"]

def sns2irc(event, context):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.connect((IRC_HOST, IRC_PORT))
    if IRC_SSL:
        irc = ssl.wrap_socket(sock)
    else:
        irc = sock
    irc.send(str.encode('PASS {}\r\n'.format(IRC_PASS)))
    irc.send(str.encode('NICK {}\r\n'.format(IRC_NICK)))
    irc.send(str.encode('USER {} {} {} :IRC2SNS\r\n'.format(IRC_NICK, IRC_NICK, IRC_NICK)))

    try:
        msg = event["Records"][0]["Sns"]["Subject"]
        if msg:
            irc.send(str.encode('PRIVMSG #{} :{}\r\n'.format(IRC_CHAN, msg[:400])))
    except KeyError:
        pass

    try:
        msg = event["Records"][0]["Sns"]["Message"].strip("\n").replace("\n", " - ")
        if msg:
            irc.send(str.encode('PRIVMSG #%s :%s\r\n' % (IRC_CHAN, msg[:400])))
    except KeyError:
        pass

