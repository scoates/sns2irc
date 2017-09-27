import irc.client, irc.connection, ssl
from ast import literal_eval
import os
from time import sleep

import logging

IRC_NICK = os.environ["IRC_NICK"]
IRC_HOST = os.environ["IRC_HOST"]
IRC_PORT = int(os.environ["IRC_PORT"])
IRC_SSL = literal_eval(os.environ["IRC_SSL"])
IRC_CHAN = os.environ["IRC_CHAN"]
IRC_PASS = os.environ["IRC_PASS"]

def sns2irc(event, context):

    request_id = context.aws_request_id

    alt_nick = IRC_NICK + "-" + request_id.split('-')[0]

    logging.debug("Event:")
    logging.debug(event["Records"][0]["Sns"])

    if 'kwargs' in event:
        channel = "#" + event['kwargs'].get('channel', IRC_CHAN)
    else:
        channel = "#" + IRC_CHAN

    logging.debug("Sending to {}".format(channel))

    if IRC_SSL:
        factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
    else:
        factory = None
    reactor = irc.client.Reactor()
    try:
        irc_client = reactor.server().connect(
            IRC_HOST,
            IRC_PORT,
            IRC_NICK,
            password=IRC_PASS,
            connect_factory=factory,
        )
    except irc.client.ServerConnectionError:
        print(sys.exc_info()[1])
        return

    def on_connect(connection, irc_event):

        try:
            msg = event["Records"][0]["Sns"]["Subject"]
            if msg:
                logging.debug("Subject> {}".format('{} :{}\r\n'.format(channel, msg[:400])))
                connection.privmsg(channel, msg)
        except KeyError:
            pass

        try:
            msg = event["Records"][0]["Sns"]["Message"].strip("\n").replace("\n", " - ")
            if msg:
                logging.debug("Message> {}".format('{} :{}\r\n'.format(channel, msg[:400])))
                connection.privmsg(channel, msg)
        except KeyError:
            pass

        connection.quit()

    def use_alt_nick(connection, irc_event):
       connection.nick(alt_nick)

    irc_client.add_global_handler("welcome", on_connect)
    irc_client.add_global_handler("nicknameinuse", use_alt_nick)

    for x in range(1, 10):
        reactor.process_once()
        sleep(0.2)

    return
