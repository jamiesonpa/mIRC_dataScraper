# This is a bot for scraping text data from mIRC channels
# This is meant to automate the task of receiving MGRS grid data,
# Decoding the 6,8, or 10 digit MGRS into a LAT/LONG
# Encoding that LAT/LONG data in an XML string
# And finally, pushing that XML string to a socket where it can be used
# To make a blip appear on a map or something like that.
# This bot was written by Pierce A. Jamieson November 2019
# This bot is written in Python v.3.7.0

import mgrs
import socket
import time
import string
from collections import defaultdict
import datetime as dt
import uuid
import xml.etree.ElementTree as ET
import socket
import logging

# mirc_server = "orwell.freenode.net"
# mirc_channel = "#dotest"
# mirc_botNick = "bot_test_parker"
# mirc_port = 6667


pubserv_IP = ""
pubserv_PORT = ""
pubserv_PROTOCOL = ""
mirc_server = ""
mirc_port = 0000
mirc_channel = ""
mirc_botNick = ""

m = mgrs.MGRS()

# Called by pushtoPubServ()


def pushUDP(ip_address, port, xml):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = sock.sendto(xml, (ip_address, port))

# Called by pushtoPubServ()


def pushTCP(ip_address, port, xml):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn = sock.connect((ip_address, port))
    sock.send(xml)

# This function pushes the xml string created in listen() to the pubserv socket. This function needs testing


def pushtoPubServ(xml_string, protocol, irc_socket, pubserv_port, pubserv_ip):
    send_message(mirc_channel, "pushing to pubserv", irc_socket)
    if protocol == "tcp":
        pushTCP(pubserv_ip, pubserv_port, xml_string)
        send_message(
            mirc_channel, "message pushed to pubserv using TCP", irc_socket)
    elif protocol == "udp":
        pushUDP(pubserv_ip, pubserv_port, xml_string)
        send_message(
            mirc_channel, "message pushed to pubserv using UDP", irc_socket)

# A simple function to find the number of times a character appears in a string


def letterOccurences(string):
    frequencies = defaultdict(lambda: 0)
    for character in string:
        frequencies[character.lower()] += 1
    return frequencies

# This is a function that sends a message to the IRC channel. This is used for debugging purposes, like print()


def send_message(chan, msg, irc_socket):
    irc_socket.send(bytes("PRIVMSG " + chan + " :" + msg + "\n", "UTF-8"))

# This is an extracted function for joining a channel in the mIRC server of interest. This is called by the listen() function


def join_channel(chan, irc_socket):
    irc_socket.send(bytes("JOIN " + chan + "\n", "UTF-8"))

# This is an extracted function for logging into mIRC. This is called by the listen() function


def login(botNick, irc_socket):
    irc_socket.send(bytes("USER " + botNick + " " + botNick +
                          " " + botNick + " " + botNick + "\n", "UTF-8"))
    irc_socket.send(bytes(("NICK " + botNick + "\n"), "UTF-8"))

# This function uses the MGRS library in python to decode the MGRS string found in the IRC string into LAT LONG and encode it in the XML format required.


def extract_grid(mgrs, irc_socket, pubserv_protocol, pubserv_port, pubserv_ip):
    splitstring = mgrs.split("$$")
    splitstring2 = splitstring[1].split("|")
    mgrs_string = splitstring2[0].strip()
    mgrs_string_gridID = mgrs_string[:5]
    mgrs_string_latlong = mgrs_string[5:]
    latlong = str(m.toLatLon(mgrs_string.encode()))
    splitlatlong = latlong.split(" ")
    lat = (((splitlatlong[0].strip()).replace(
        ",", "")).replace(")", "")).replace("(", "")
    _long = (((splitlatlong[1].strip()).replace(
        ",", "")).replace(")", "")).replace("(", "")
    clocktime = time.strftime("%R")
    xmltranslation = "<?xml version='1.0' standalone='yes'?><event version= " + \
        "\"" + str("2.0") + "\"" + " uid= " "\"" + "\"" + " time=" + "\"" + clocktime + "\"" + "><detail></detail><point lat=" + \
        "\"" + lat + "\"" + " lon= " + "\"" + _long + "\"" + "/></event>"
    send_message(mirc_channel, "XML Translation: " +
                 xmltranslation, irc_socket)
    pushtoPubServ(xmltranslation, pubserv_protocol,
                  irc_socket, pubserv_port, pubserv_ip)

# This block contains a while loop that is constantly listening for strings of interest on the IRC channel chosen by the user.


def listen(irc_server, irc_channel, irc_nick, irc_port, pubserv_protocol, pubserv_ip, pubserv_port):
    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_socket.connect((mirc_server, irc_port))
    login(irc_nick, irc_socket)
    join_channel(mirc_channel, irc_socket)
    connected = True
    ircmsg = ""
    while connected == True:
        log = open("log.txt", "a")
        ircmsg = irc_socket.recv(2048).decode("UTF-8")
        ircmsg = ircmsg.strip('\n\r')
        print(ircmsg)
        if ircmsg != "":
            delimFreq = letterOccurences(str(ircmsg))
            if delimFreq["$"] >= 2:
                send_message(
                    mirc_channel, "string of interest identified", irc_socket)
                extract_grid(str(ircmsg), irc_socket,
                             pubserv_protocol, pubserv_port, pubserv_ip)
                log.write(str(ircmsg)+"\n")
                log.close()
            else:
                pass


# This block runs first and allows the user to configure the IP, ports, etc.
print("******* INITIALIZING IRC RELAY *******")
check_default = input("USE DEFAULT mIRC CHANNEL SETTINGS? (y/n):")
if check_default == "y":
    mirc_server = "orwell.freenode.net"
    mirc_channel = "#dotest"
    mirc_botNick = "bot_test_parker"
    mirc_port = 6667
else:
    mirc_server = input("PROVIDE IRC HOSTNAME:")
    mirc_port = input("PROVIDE IRC PORT:")
    mirc_port = int(mirc_port)
    mirc_botNick = input("PROVIDE IRC NICK")
    mirc_channel = input("PROVIDE IRC CHANNEL (#CHANNEL_NAME):")

pubserv_IP = input("PROVIDE PUBSERV IP:")
pubserv_PORT = input("PROVIDE PUBSERV PORT:")
pubserv_PORT = int(pubserv_PORT)
pubserv_PROTOCOL = input("PROVIDE PUBSERV PROTOCOL (tcp/udp):")
print("\n")
print("\n")
print("*************************************")
print("*********SETTINGS CONFIGURED*********")
print("IRC SERVER: " + mirc_server)
print("IRC CHANNEL: " + mirc_channel)
print("IRC NICK: " + mirc_botNick)
print("PUBSERV IP: " + pubserv_IP)
print("PUBSERV PORT: " + str(pubserv_PORT))
print("PUBSERV PROTOCOL: " + pubserv_PROTOCOL)
print("*************************************")
print("*************************************")
print("CONNECTING TO IRC...")
print("...\n")
print("...\n")
listen(mirc_server, mirc_channel, mirc_botNick, mirc_port,
       pubserv_PROTOCOL, pubserv_IP, pubserv_PORT)
