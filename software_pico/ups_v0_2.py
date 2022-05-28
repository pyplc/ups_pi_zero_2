#
# MicroPython ups_v0_2.py
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

from machine import Pin, I2C, UART, Timer, ADC
from sh1106 import SH1106_I2C
from time import sleep, ticks_ms
#import machine
import os

uart = UART(0, 9600, tx=Pin(0), rx=Pin(1))
print(uart)

b = None
msg = ""

# ananlogwert von Li ion Zelle
analog_value = ADC(28)

#spannungsüberwachung eingang GPIO2
I2 = Pin(2, Pin.IN)

# lion akku power pin
lion_power_on = Pin(4, Pin.OUT, value=0) # set pin high on creation
lion_power_on.value(1)

# pi power pin
pi_power_on = Pin(5, Pin.OUT, value=0) # set pin high on creation
pi_power_on.value(0)

# Lade IC power on pin
charger_ic_on = Pin(6, Pin.OUT, value=0) # set pin high on creation
charger_ic_on.value(1)

# i2c Bus aktivieren
i2c = I2C(1, scl=Pin(27), sda=Pin(26))

# oled
WIDTH  = 128                                            # oled display width
HEIGHT = 64                                          # oled display height
oled = SH1106_I2C(WIDTH, HEIGHT, i2c)                  # Init oled display

oled.fill(0)
oled.text('booting', 0, 0)
oled.show()

ups_status = 1
minimum_zeit_pi_start = 1
minimum_zeit_pi_start_on = False
power_ein_zeit_warten = 1
power_off_zeit_warten = 1
sek_counter = 0
volt_lion = 0.0
b = None
msg = ""

# Will return a float
def convert_float(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Will return a integer
def convert_int(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def show_oled():
    oled.fill(0)
    zeile_1 = 'I: ' + str(I2.value())
    oled.text(zeile_1, 0, 0)
    zeile_2 = str(msg)
    oled.text(zeile_2, 0, 15)
    zeile_3 = str(volt_lion) + ' V'
    oled.text(zeile_3, 0, 30)
    zeile_4 = 'status: ' + str(ups_status)
    oled.text(zeile_4, 0, 42)
    zeile_5 = 'Q: ' + str(sek_counter)
    oled.text(zeile_5, 0, 55)
    oled.show()

while True:
    #convert_float(x, in_min, in_max, out_min, out_max)
    reading = analog_value.read_u16()
    volt_lion = convert_float(reading, 0, 65500, 0, 5.5)
    #print("ADC: ",volt_lion)
    
    # Power zustand an pi melden 1 = ok, 0 = no power
    #uart.write(str(I2.value()))
        
    #eine kleine Pause von 100 Millisekunden
    if uart.any():
        b = uart.readline()
        #print(type(b))
        #print(b)
        try:
            msg = b.decode('utf-8')
            #print(type(msg))
            #print(">> " + msg)
            #show_oled()
        except:
            pass
        
    sek_counter += 1

    if minimum_zeit_pi_start_on:
        minimum_zeit_pi_start += 1
        if minimum_zeit_pi_start >= 200:
            minimum_zeit_pi_start = 200
            
    # 1 Power ein, warte 10 sek
    if ups_status == 1:
        power_ein_zeit_warten += 1
        if power_ein_zeit_warten >= 10:
            if I2.value() == 0:
                lion_power_on.value(0)
                sleep(2)
            print('power ein zeit abgelaufen')
            power_ein_zeit_warten = 0
            ups_status = 2

    # 2 Lion Battery einschalten, minimum Zeit start Pi setzen
    if ups_status == 2:
        minimum_zeit_pi_start_on = True
        ups_status = 3

    # 3 Pi Zero ein
    if ups_status == 3:
        print('start pi')
        pi_power_on.value(1)
        ups_status = 4
        
    # 4 Normalbetrieb, abfrage ob Power ok, nok = 5
    if ups_status == 4:
        #abfrage ob Power ok
        if I2.value() == 0:
            ups_status = 5
            
    # warte 10 sek ob Power ok, nok = 10, ok = 4
    if ups_status == 5:
        power_ein_zeit_warten += 1
        if power_ein_zeit_warten >= 10:
            if I2.value() == 1:
                ups_status = 4
                power_ein_zeit_warten = 0
            else:
                power_ein_zeit_warten = 0
                ups_status = 10
    
    # 10 warte bis minimum Zeit Pi start abgelaufen > ja = 11, nein = 5
    if ups_status == 10:
        if minimum_zeit_pi_start >= 60:
            ups_status = 11
        else:
            ups_status = 5
    
    # 11 Komado Pi runterfahren
    if ups_status == 11:
        # Power zustand an pi melden 1 = ok, 0 = no power
        #uart.write(str(I2.value()))
        uart.write('0')
        ups_status = 12
        
    # 12 Warte bis PI vollständig rutergefahren
    if ups_status == 12:
        power_off_zeit_warten += 1
        if power_off_zeit_warten >= 30:
            power_off_zeit_warten = 0
            ups_status = 13
            
    # 13 Pi Zero aus, warte 5 sek
    if ups_status == 13:
        pi_power_on.value(0)
        power_off_zeit_warten += 1
        if power_off_zeit_warten >= 5:
            power_off_zeit_warten = 0
            ups_status = 14
        
    # 14 abfrage Power ok, ok = 1, nok = 15
    if ups_status == 14:
        #abfrage ob Power ok
        if I2.value() == 1:
            ups_status = 1
        else:
            ups_status = 15
    
    # 15 ups auschalten, Ende
    if ups_status == 15:
        lion_power_on.value(0)
        
    #print(sek_counter)
    show_oled()
    sleep(1)
