#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
import serial
import time
import sys

# ttyS0 for RX,TX pin
# ser = serial.Serial('/dev/ttyS0', 115200)

# ttyUSB2 for USB channel (For SIM7600G-H 4G Dongle recommend ttyUSB2)
ser = serial.Serial('/dev/ttyUSB2', 115200)

ser.flushInput()

power_key = 6
rec_buff = ''
rec_buff2 = ''
time_count = 0

def send_at(command, back, timeout):
    rec_buff = ''
    ser.write((command+'\r\n').encode())
    time.sleep(timeout)
    if ser.inWaiting():
        time.sleep(0.01)
        rec_buff = ser.read(ser.inWaiting())
    if rec_buff != '':
        if back not in rec_buff.decode():
        #     print(command + ' ERROR')
        #     print(command + ' back:\t' + rec_buff.decode())
            return 0
        else:

            # print(rec_buff.decode())

            # Additions to Demo Code Written by Tim!
            global GPSDATA

            GPSDATA = str(rec_buff.decode())
            Cleaned = GPSDATA[13:]
            # GPS NMEA format
            print('Cleaned : ',Cleaned)

            if command == 'AT+CGPSINFO' :
                x = Cleaned.split(' ')
                y = x[0].split(',')

                # GPS is 0.0 until it gets the position.
                if y[0] == '' :
                    lat = 0.0
                    lng = 0.0
                else:
                    a = y[0][0:2]  # lat
                    b = y[2][0:3]  # long
                    c = y[0][2:]  # small lat
                    d = y[2][3:]  # small long
                    nos = y[1]
                    eow = y[3]

                    lat = float(a) + (float(c)/60)
                    lng = float(b) + (float(d)/60)
                    if nos == 'S':
                        lat = -lat
                    if eow == 'W':
                        lng = -lng

            dicts = dict()

            if lat == 0.0:
                dicts['lat'] = 0.0
                dicts['long'] = 0.0
            else:
                dicts['lat'] = float("{:.5f}".format(lat))
                dicts['long'] = float("{:.5f}".format(lng))
                
            print('Latitude : '+str(dicts['lat'])+'\nLongitude : '+str(dicts['long']))

            return 1
    else:
        print('GPS is not ready')
        return 0

# Wait for connection
time.sleep(30) 
# Open GPS command
send_at('AT+CGPS=1,1', 'OK', 1)

while True:
    try:
        # Recieve GPS location every 30 second
        send_at('AT+CGPSINFO', '+CGPSINFO: ', 1)
        time.sleep(30)

    except KeyboardInterrupt :
        print('Keyboard interrupt.')
        sys.exit(1)

