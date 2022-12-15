#(2021) Jonathan Williams (z5162987)
#Purpose:
##Recieves data from sensor via BLE channel
##Saves data to csv file
#Usage:
##Use with the SensorReadings Arduino sketch

import os
import asyncio
from bleak import BleakClient
from bleak import _logger as logger

CHARACTERISTIC_UUID = "0000FFF1-0000-1000-8000-00805F9B34FB"
ADDRESS = "EC:91:1A:14:E3:84" #address for Adruino
global buffer
buffer = ""

FILENAME = "acc_1_1.csv"
f = open(FILENAME, "w")
#For sensor data:
f.write("x,y,z\n")
#For Madgwick data:
#f.write("t,acc,qw,qx,qy,qz,px,py,pz\n")

#returns sensor data in format "x,y,z"
def parse_sensor_data(data):
    [x, y, z] = data[:-1].split()
    return "{},{},{}\n".format(x,y,z)

#returns madgwick data in format "time,acceleration_magnitude,qw,qx,qy,qz,posx,posy,posz"
def parse_madgwick_data(data):
    #remove leading 'Mov:'
    data = data[6:]
    #remove trailing '#'
    data = data[:-1]
    #remove ' and ;
    data = data.replace(",", "") 
    data = data.replace(";", "") 
    [t,acc,qw,qx,qy,qz,posx,posy,posz] = data.split()
    return "{},{},{},{},{},{},{},{},{}\n".format(t,acc,qw,qx,qy,qz,posx,posy,posz)

def notification_handler(sender, data):
    #print("BLE Channel Recieved::: {0}: {1}".format(sender, data))
    global buffer
    #remove BLE header
    buffer += str(data)[12:-2]
    if buffer[-1] == '#':
        parsed_data = parse_sensor_data(buffer)
        #parsed_data = parse_madgwick_data(buffer)
        print(parsed_data)
        f.write(parsed_data)
        buffer = ""

async def run(address):
    async with BleakClient(address) as client:
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        while await client.is_connected():
            await asyncio.sleep(1)
        print("Closing file")    
        f.close()

if __name__ == "__main__":
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(ADDRESS))
