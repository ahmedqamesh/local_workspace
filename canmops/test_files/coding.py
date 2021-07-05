import numpy as np
import sys
import struct
import signal
import time
from tqdm import tqdm
from colorama import Fore
import os
from sys import stdout
from time import sleep
from collections import deque, Counter
# #textboxValue = [40, 0, 10, 0, 0, 0, 0, 0]
textboxValue = [0, 10]#, 0, 0, 0, 0]
# textboxValue = ["40", "0", "10", "0", "0", "0", "0", "0"]
bytes_hex = [int(str(b), 16) for b in textboxValue]
#bytes_hex = list(map(int, textboxValue))
# original = bytearray(b'\x00P\x80\xfe\x01(\x02\x00')
ioriginal = int.from_bytes(bytes_hex, byteorder=sys.byteorder)

# b1, b2, b3, b4, b5, b6, b7, b8 = ioriginal.to_bytes(8, 'little')
# print(hex(b1)[2:], hex(b2)[2:], hex(b3)[2:], hex(b4)[2:], hex(b5)[2:], hex(b6)[2:], hex(b7)[2:], hex(b8)[2:])
# print([f'{b1:02x} {b2:02x} {b3:02x} {b4:02x} {b5:02x} {b6:02x} {b7:02x} {b8:02x}'])
# x = input('CAN Interface:')
# print('Hello, ' + x)
# while True:    
#     os.system("cansend can0 601#1122334455667788")
#     print("cansend can0")
#     time.sleep(1)
#os.system("gnome-terminal -x python candump.py &")
command="candump can0"
os.system("gnome-terminal -e 'bash -c \""+command+";bash\"'")


