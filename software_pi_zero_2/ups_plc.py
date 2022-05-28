#
# MicroPython ups_plc.py
#
# The MIT License (MIT)
#
# Copyright (c) 2022 Herbert Schneider
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import time
import serial
import os

ser = serial.Serial(
  port='/dev/ttyS0', # Change this according to connection methods, e.g. /dev/ttyUSB0
  #port='/dev/ttyAMA0', # Change this according to connection methods, e.g. /dev/ttyUSB0
  baudrate = 9600,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1)

print("init fertig")

msg = ""
i = 0
ii = ''
cmd_shootdown = 0

while True:
    #shootdown cmd
    if cmd_shootdown == 1:
        continue
    
    i+=1
    ii = ser.read()
    print(ii.decode('utf-8'))
    print("Counter {} - Hello from Raspberry Pi".format(i))
    #payload = 'hello ' + str(i)
    payload = str(i)
    #ser.write(payload.encode('utf-8'))
    ser.write(payload.encode('utf-8'))
    
    if ii.decode('utf-8') == '0' and cmd_shootdown == 0:
        payload = 'shootdown'
        #ser.write(payload.encode('utf-8'))
        ser.write(payload.encode('utf-8'))
        os.popen("sudo poweroff")
        print("PI wird Runtergefahren")
        cmd_shootdown = 1
        time.sleep(2)
        
    time.sleep(1)
