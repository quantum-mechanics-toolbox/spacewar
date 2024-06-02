#!/usr/bin/env python3

import RPi.GPIO as GPIO
import board
import digitalio
import busio
import time

print("Hello, blinka!")

# Try to create a Digital input
pin = digitalio.DigitalInOut(board.D4)
print("Digital IO ok!")

# Try to create an I2C device
i2c = busio.I2C(board.SCL, board.SDA)
print("I2C ok!")

# Try to create an SPI device
spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
print("SPI ok!")

# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

#import busio
#import digitalio
#import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D5)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)





# create an analog input channel on pin 0
starttime = time.time()
chan0 = AnalogIn(mcp, MCP.P0)
lastval0 = chan0.value
print("{}\t{}".format(lastval0, starttime))

maxhigh = 0.0

while True:
    val0 = chan0.value
    difftime = time.time()-starttime
    diff0 = val0-lastval0
    if abs(diff0)>577:
        print("{: 0.3f}\t{}".format(val0, difftime))
    lastval0 = val0
 
#    print(chan0.value, chan1.value, chan2.value, chan3.value)
    #    print("Raw ADC Value: ", chan.value, "ADC Voltage: " + str(chan.voltage) + "V")
#    print("Raw ADC Value: ", chan.value, )
#    print("ADC Voltage: " + str(chan.voltage) + "V")
#    time.sleep(0.25)





print("done!")
