#(2021) Jonathan Williams (z5162987)
#Purpose:
##Recieves data from sensor via BLE channel
##Sends data to Unity script via TCP connection
#Usage:
##Use with the MotionFollower Arduino sketch
##Run Unity script once this prints "Initialising TCP connection"

import os
import asyncio
import socket
from bleak import BleakClient

CHARACTERISTIC_UUID = "0000FFF1-0000-1000-8000-00805F9B34FB"
ADDRESS = "EC:91:1A:14:E3:78" #address for Arduino
HOST = '127.0.0.1'
PORT = 65432  
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind((HOST, PORT))
soc.settimeout(15)
global buffer
buffer = ""

def init_tcp():
    print("Initialising TCP connection")
    soc.listen()
    global conn
    conn, addr = soc.accept()
    print("connected to {}".format(addr))

def notification_handler(sender, data):
    #print("BLE Channel Recieved::: {0}: {1}".format(sender, data))
    global buffer 
    buffer += str(data)[12:-2]
    if buffer[-1] == '#':
        print("Sending {} to unity client".format(buffer))
        conn.sendall(bytes(buffer,"utf8"))
        buffer = ""

async def run(address):
    async with BleakClient(address) as client:
        init_tcp()
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        while await client.is_connected():
            await asyncio.sleep(0.001)

if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(ADDRESS))
