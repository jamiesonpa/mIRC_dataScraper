# This is a bot for scraping text data from mIRC channels
# This bot was written by Pierce A. Jamieson 10_1_2018
# This bot is written in Python v.3.7.0


import socket
import time
import string
import string
from collections import defaultdict

server = "SERVER_NAME"
channel = "#CHANNELNAME"
botNick = "NICKNAME"

# This allows me to search through strings for certain letters


def letterOccurences(string):
    frequencies = defaultdict(lambda: 0)
    for character in string:
        frequencies[character.lower()] += 1
    return frequencies

# This allows me to respond to server pings


def ping():
    irc_socket.send(bytes("PONG :pingis\n", "UTF-8"))

# This allows me to send encoded messages to IRC


def send_message(chan, msg):
    irc_socket.send(bytes("PRIVMSG " + chan + " :" + msg + "\n", "UTF-8"))


def join_channel(chan):
    irc_socket.send(bytes("JOIN " + chan + "\n", "UTF-8"))

# can change these "botnick" placeholders later


def login():
    irc_socket.send(bytes("USER " + botNick + " " + botNick +
                          " " + botNick + " " + botNick + "\n", "UTF-8"))
    irc_socket.send(bytes(("NICK " + botNick + "\n"), "UTF-8"))


# this is the main function
irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc_socket.connect((server, 6667))
login()
join_channel(channel)
connected = True
ircmsg = ""
while connected == True:
    log = open("log.txt", "a")
    ircmsg = irc_socket.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg+"\n")
    if ircmsg != "":
        delimFreq = letterOccurences(str(ircmsg))
        if delimFreq["|"] >= 2:
            send_message(channel, "string of interest identified")
            log.write(str(ircmsg)+"\n")
            log.close()
        else:
            pass
