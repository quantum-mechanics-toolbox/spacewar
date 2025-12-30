#!/usr/bin/env python3

import board
import digitalio
import busio
import time

print("Hello, blinka!")

# Try to create a Digital input
# pin = digitalio.DigitalInOut(board.D4)
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
chan0 = AnalogIn(mcp, MCP.P0)
chan1 = AnalogIn(mcp, MCP.P1)
chan2 = AnalogIn(mcp, MCP.P2)
chan3 = AnalogIn(mcp, MCP.P3)
chan4 = AnalogIn(mcp, MCP.P4)
chan5 = AnalogIn(mcp, MCP.P5)
chan6 = AnalogIn(mcp, MCP.P6)
chan7 = AnalogIn(mcp, MCP.P7)

lastval0 = chan0.value/65535
lastval1 = chan1.value/65535
lastval2 = chan2.value/65535
lastval3 = chan3.value/65535
lastval4 = chan4.value/65535
lastval5 = chan5.value/65535
maxhigh = 0.0

while True:
    val0 = chan0.value/65535
    val1 = chan1.value/65535
    val2 = chan2.value/65535
    val3 = chan3.value/65535
    val4 = chan4.value/65535
    val5 = chan5.value/65535

    diff0 = val0-lastval0
    diff1 = val1-lastval1
    diff2 = val2-lastval2
    diff3 = val3-lastval3
    diff4 = val4-lastval4
    diff5 = val5-lastval5
    
    maxdiff = max(abs(diff0), abs(diff1), abs(diff2), abs(diff3), abs(diff4), abs(diff5))
    maxhigh = max(maxdiff, maxhigh)
    avediff = (abs(diff0) + abs(diff1) + abs(diff2) + abs(diff3) + abs(diff4) + abs(diff5))/6
    
    print("{: 0.3f}\t{: 0.3f}\t{: 0.3f}\t{: 0.3f}\t{: 0.3f}\t{: 0.3f}".format(val0, val1, val2, val3, val4, val5))
    print("{: 0.3f}\t{: 0.3f}\t{: 0.3f}\t{: 0.3f}\t{: 0.3f}\t{: 0.3f}".format(val0-lastval0, val1-lastval1, val2-lastval2, val3-lastval3, val4-lastval4, val5-lastval5))
    print("MAX: {:0.3f}\t AVE: {:0.3f}\t\tMAX HIGH: {:0.3f} : {:d}".format(maxdiff, avediff, maxhigh, int(maxhigh*65535)))

    lastval0 = val0
    lastval1 = val1
    lastval2 = val2
    lastval3 = val3
    lastval4 = val4
    lastval5 = val5

#    print(chan0.value, chan1.value, chan2.value, chan3.value)
    #    print("Raw ADC Value: ", chan.value, "ADC Voltage: " + str(chan.voltage) + "V")
#    print("Raw ADC Value: ", chan.value, )
#    print("ADC Voltage: " + str(chan.voltage) + "V")
    time.sleep(0.25)





print("done!")
