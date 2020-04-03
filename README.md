# micropython-fingerprint
[MicroPython](https://micropython.org/) library for reading ZhianTec finger print sensors.

This MicroPython library is based on the original [pyfingerprint](https://github.com/bastianraschke/pyfingerprint)
for the Raspberry Pi and has the same [German free software license](http://www.d-fsl.org).

As with the original library it should work with ZFM-20, ZFM-60, etc sensors. I have been testing with the R503 sensor.

It appears to be working, but I have not yet verified all the functionality

A small test program to verify that the sensor is communicating. Depending on
what development board is in use, the UART instance may have to be differently
configured. Note that the baud rate MUST be a multiple of 9600.
```
from pyfingerprint import PyFingerprint
from machine import UART

sensorSerial = UART(1)
sensorSerial.init(57600, bits=8, parity=None, stop=1, rx=13, tx=12)

f = PyFingerprint(sensorSerial)
f.verifyPassword()
```
