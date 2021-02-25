import sys
import getopt
import socket
from time import sleep
import threading
import math

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 1790))


msg = str.encode('a' * 1024)
while True:
    sent = s.send(msg)
    if sent == 0:
        raise RuntimeError("socket connection broken")
