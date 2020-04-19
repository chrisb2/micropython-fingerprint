# micropython-fingerprint
[MicroPython](https://micropython.org/) library for reading ZhianTec finger print sensors.

This MicroPython library is a slightly modified version of the [pyfingerprint](https://github.com/bastianraschke/pyfingerprint)
for the Raspberry Pi and has the same [German free software license](http://www.d-fsl.org).

As with the original library it should work with ZFM-20, ZFM-60, etc sensors. I have been testing with the R503 sensor.

A small test program to verify that the sensor is communicating. Depending on
what development board is in use, the UART instance may have to be differently
configured. Note that the baud rate MUST be a multiple of 9600.
```
from pyfingerprint import PyFingerprint
from machine import UART

sensorSerial = UART(1)
# ESP32 (pins 12, 13)
sensorSerial.init(57600, bits=8, parity=None, stop=1, rx=13, tx=12)
# pyboard v1.1 (pins X9, X10)
# sensorSerial.init(57600, bits=8, parity=None, stop=1)

f = PyFingerprint(sensorSerial)
f.verifyPassword() # should return True
```

Further example programs which should be easily adapted can be found with the original [pyfingerprint](https://github.com/bastianraschke/pyfingerprint/tree/Development/src/files/examples) library.

# Trouble Shooting

## Download characteristics packet corruption
```
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "pyfingerprint.py", line 1461, in downloadCharacteristics
  File "pyfingerprint.py", line 372, in __readPacket
Exception: The received packet is corrupted (the checksum is wrong)!
```
Solution - reduce baud rate

# Documentation

* [pyfingerprint](#.pyfingerprint)
  * [FINGERPRINT\_SETSYSTEMPARAMETER\_BAUDRATE](#.pyfingerprint.FINGERPRINT_SETSYSTEMPARAMETER_BAUDRATE)
  * [FINGERPRINT\_SETSYSTEMPARAMETER\_SECURITY\_LEVEL](#.pyfingerprint.FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL)
  * [FINGERPRINT\_SETSYSTEMPARAMETER\_PACKAGE\_SIZE](#.pyfingerprint.FINGERPRINT_SETSYSTEMPARAMETER_PACKAGE_SIZE)
  * [FINGERPRINT\_LED\_BREATHING](#.pyfingerprint.FINGERPRINT_LED_BREATHING)
  * [FINGERPRINT\_LED\_FLASHING](#.pyfingerprint.FINGERPRINT_LED_FLASHING)
  * [FINGERPRINT\_LED\_CONTINUOUS](#.pyfingerprint.FINGERPRINT_LED_CONTINUOUS)
  * [FINGERPRINT\_LED\_OFF](#.pyfingerprint.FINGERPRINT_LED_OFF)
  * [FINGERPRINT\_LED\_GRADUAL\_ON](#.pyfingerprint.FINGERPRINT_LED_GRADUAL_ON)
  * [FINGERPRINT\_LED\_GRADUAL\_OFF](#.pyfingerprint.FINGERPRINT_LED_GRADUAL_OFF)
  * [FINGERPRINT\_LED\_RED](#.pyfingerprint.FINGERPRINT_LED_RED)
  * [FINGERPRINT\_LED\_BLUE](#.pyfingerprint.FINGERPRINT_LED_BLUE)
  * [FINGERPRINT\_LED\_PURPLE](#.pyfingerprint.FINGERPRINT_LED_PURPLE)
  * [FINGERPRINT\_CHARBUFFER1](#.pyfingerprint.FINGERPRINT_CHARBUFFER1)
  * [FINGERPRINT\_CHARBUFFER2](#.pyfingerprint.FINGERPRINT_CHARBUFFER2)
  * [PyFingerprint](#.pyfingerprint.PyFingerprint)
    * [\_\_init\_\_](#.pyfingerprint.PyFingerprint.__init__)
    * [\_\_del\_\_](#.pyfingerprint.PyFingerprint.__del__)
    * [verifyPassword](#.pyfingerprint.PyFingerprint.verifyPassword)
    * [setPassword](#.pyfingerprint.PyFingerprint.setPassword)
    * [setAddress](#.pyfingerprint.PyFingerprint.setAddress)
    * [setSystemParameter](#.pyfingerprint.PyFingerprint.setSystemParameter)
    * [setBaudRate](#.pyfingerprint.PyFingerprint.setBaudRate)
    * [setSecurityLevel](#.pyfingerprint.PyFingerprint.setSecurityLevel)
    * [setMaxPacketSize](#.pyfingerprint.PyFingerprint.setMaxPacketSize)
    * [getSystemParameters](#.pyfingerprint.PyFingerprint.getSystemParameters)
    * [getStorageCapacity](#.pyfingerprint.PyFingerprint.getStorageCapacity)
    * [getSecurityLevel](#.pyfingerprint.PyFingerprint.getSecurityLevel)
    * [getMaxPacketSize](#.pyfingerprint.PyFingerprint.getMaxPacketSize)
    * [getBaudRate](#.pyfingerprint.PyFingerprint.getBaudRate)
    * [getTemplateIndex](#.pyfingerprint.PyFingerprint.getTemplateIndex)
    * [getTemplateCount](#.pyfingerprint.PyFingerprint.getTemplateCount)
    * [readImage](#.pyfingerprint.PyFingerprint.readImage)
    * [convertImage](#.pyfingerprint.PyFingerprint.convertImage)
    * [createTemplate](#.pyfingerprint.PyFingerprint.createTemplate)
    * [storeTemplate](#.pyfingerprint.PyFingerprint.storeTemplate)
    * [searchTemplate](#.pyfingerprint.PyFingerprint.searchTemplate)
    * [loadTemplate](#.pyfingerprint.PyFingerprint.loadTemplate)
    * [deleteTemplate](#.pyfingerprint.PyFingerprint.deleteTemplate)
    * [clearDatabase](#.pyfingerprint.PyFingerprint.clearDatabase)
    * [compareCharacteristics](#.pyfingerprint.PyFingerprint.compareCharacteristics)
    * [uploadCharacteristics](#.pyfingerprint.PyFingerprint.uploadCharacteristics)
    * [generateRandomNumber](#.pyfingerprint.PyFingerprint.generateRandomNumber)
    * [downloadCharacteristics](#.pyfingerprint.PyFingerprint.downloadCharacteristics)
    * [softReset](#.pyfingerprint.PyFingerprint.softReset)
    * [checkSensor](#.pyfingerprint.PyFingerprint.checkSensor)
    * [handshake](#.pyfingerprint.PyFingerprint.handshake)
    * [cancelInstruction](#.pyfingerprint.PyFingerprint.cancelInstruction)
    * [ledOn](#.pyfingerprint.PyFingerprint.ledOn)
    * [ledOff](#.pyfingerprint.PyFingerprint.ledOff)

<a name=".pyfingerprint"></a>
## pyfingerprint

PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

<a name=".pyfingerprint.FINGERPRINT_SETSYSTEMPARAMETER_BAUDRATE"></a>
#### FINGERPRINT\_SETSYSTEMPARAMETER\_BAUDRATE

Set the baud rate.

<a name=".pyfingerprint.FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL"></a>
#### FINGERPRINT\_SETSYSTEMPARAMETER\_SECURITY\_LEVEL

Set the security level.

<a name=".pyfingerprint.FINGERPRINT_SETSYSTEMPARAMETER_PACKAGE_SIZE"></a>
#### FINGERPRINT\_SETSYSTEMPARAMETER\_PACKAGE\_SIZE

Set the package size.

<a name=".pyfingerprint.FINGERPRINT_LED_BREATHING"></a>
#### FINGERPRINT\_LED\_BREATHING

Breathing LED.

<a name=".pyfingerprint.FINGERPRINT_LED_FLASHING"></a>
#### FINGERPRINT\_LED\_FLASHING

Flashing LED.

<a name=".pyfingerprint.FINGERPRINT_LED_CONTINUOUS"></a>
#### FINGERPRINT\_LED\_CONTINUOUS

Continuous LED.

<a name=".pyfingerprint.FINGERPRINT_LED_OFF"></a>
#### FINGERPRINT\_LED\_OFF

LED off.

<a name=".pyfingerprint.FINGERPRINT_LED_GRADUAL_ON"></a>
#### FINGERPRINT\_LED\_GRADUAL\_ON

Turn LED on gradually.

<a name=".pyfingerprint.FINGERPRINT_LED_GRADUAL_OFF"></a>
#### FINGERPRINT\_LED\_GRADUAL\_OFF

Turn LED off gradually.

<a name=".pyfingerprint.FINGERPRINT_LED_RED"></a>
#### FINGERPRINT\_LED\_RED

Red LED.

<a name=".pyfingerprint.FINGERPRINT_LED_BLUE"></a>
#### FINGERPRINT\_LED\_BLUE

Blue LED.

<a name=".pyfingerprint.FINGERPRINT_LED_PURPLE"></a>
#### FINGERPRINT\_LED\_PURPLE

Purple LED.

<a name=".pyfingerprint.FINGERPRINT_CHARBUFFER1"></a>
#### FINGERPRINT\_CHARBUFFER1

Char buffer 1

<a name=".pyfingerprint.FINGERPRINT_CHARBUFFER2"></a>
#### FINGERPRINT\_CHARBUFFER2

Char buffer 2

<a name=".pyfingerprint.PyFingerprint"></a>
### PyFingerprint

```python
class PyFingerprint(object)
```

Manages ZhianTec fingerprint sensors.

<a name=".pyfingerprint.PyFingerprint.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(uart, address=0xFFFFFFFF, password=0x00000000)
```

Constructor.

**Arguments**:

- `uart` - Instance of machine.UART. The baud rate set in the UART
  instance MUST be a multiple of 9600. Passing in a UART instance
  enables different flavors of MicroPython to be supported.
- `address` _int_ - The sensor address
- `password` _int_ - The sensor password


**Raises**:

- `ValueError` - if address or password are invalid

<a name=".pyfingerprint.PyFingerprint.__del__"></a>
#### \_\_del\_\_

```python
 | __del__()
```

Destructor.

<a name=".pyfingerprint.PyFingerprint.verifyPassword"></a>
#### verifyPassword

```python
 | verifyPassword()
```

Verifies password of the sensor.

**Returns**:

  True if password is correct or False otherwise.


**Raises**:

- `Exception` - if an error occured

<a name=".pyfingerprint.PyFingerprint.setPassword"></a>
#### setPassword

```python
 | setPassword(newPassword)
```

Sets the password of the sensor.

**Arguments**:

- `newPassword` _int_ - The new password to use.


**Returns**:

  True if password was set correctly or False otherwise.


**Raises**:

- `Exception` - if an error occured

<a name=".pyfingerprint.PyFingerprint.setAddress"></a>
#### setAddress

```python
 | setAddress(newAddress)
```

Sets the sensor address.

**Arguments**:

- `newAddress` _int_ - The new address to use.


**Returns**:

  True if address was set correctly or False otherwise.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.setSystemParameter"></a>
#### setSystemParameter

```python
 | setSystemParameter(parameterNumber, parameterValue)
```

Set a system parameter of the sensor.

**Arguments**:

- `parameterNumber` _int_ - The parameter number. Use one of `FINGERPRINT_SETSYSTEMPARAMETER_*` constants.
- `parameterValue` _int_ - The value


**Returns**:

  True if successful or False otherwise.


**Raises**:

- `ValueError` - if any passed parameter is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.setBaudRate"></a>
#### setBaudRate

```python
 | setBaudRate(baudRate)
```

Sets the baud rate.

**Arguments**:

- `baudRate` _int_ - The baud rate


**Raises**:

- `ValueError` - if passed baud rate is no multiple of 9600
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.setSecurityLevel"></a>
#### setSecurityLevel

```python
 | setSecurityLevel(securityLevel)
```

Sets the security level of the sensor.

**Arguments**:

- `securityLevel` _int_ - Value between 1 and 5 where 1 is lowest and 5 highest.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.setMaxPacketSize"></a>
#### setMaxPacketSize

```python
 | setMaxPacketSize(packetSize)
```

Sets the maximum packet size of sensor.

**Arguments**:

- `packetSize` _int_ - 32, 64, 128 and 256 are supported.


**Raises**:

- `ValueError` - if passed packet size is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.getSystemParameters"></a>
#### getSystemParameters

```python
 | getSystemParameters()
```

Gets all available system information of the sensor.

**Returns**:

  A tuple that contains the following information:
- `0` - integer(2 bytes) The status register.
- `1` - integer(2 bytes) The system id.
- `2` - integer(2 bytes) The storage capacity.
- `3` - integer(2 bytes) The security level.
- `4` - integer(4 bytes) The sensor address.
- `5` - integer(2 bytes) The packet length.
- `6` - integer(2 bytes) The baud rate.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.getStorageCapacity"></a>
#### getStorageCapacity

```python
 | getStorageCapacity()
```

Gets the sensor storage capacity.

**Returns**:

  The storage capacity (int).


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.getSecurityLevel"></a>
#### getSecurityLevel

```python
 | getSecurityLevel()
```

Gets the security level of the sensor.

**Returns**:

  The security level (int).


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.getMaxPacketSize"></a>
#### getMaxPacketSize

```python
 | getMaxPacketSize()
```

Gets the maximum allowed size of a single packet.

**Returns**:

  Return the max size (int).


**Raises**:

- `ValueError` - if packet size is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.getBaudRate"></a>
#### getBaudRate

```python
 | getBaudRate()
```

Gets the baud rate.

**Returns**:

  The baud rate (int).


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.getTemplateIndex"></a>
#### getTemplateIndex

```python
 | getTemplateIndex(page)
```

Gets a list of the template positions with usage indicator.

**Arguments**:

- `page` _int_ - The page (value between 0 and 3).


**Returns**:

  The list.


**Raises**:

- `ValueError` - if passed page is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.getTemplateCount"></a>
#### getTemplateCount

```python
 | getTemplateCount()
```

Gets the number of stored templates.

**Returns**:

  The template count (int).


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.readImage"></a>
#### readImage

```python
 | readImage()
```

Reads the image of a finger and stores it in image buffer.

**Returns**:

  True if image was read successfully or False otherwise.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.convertImage"></a>
#### convertImage

```python
 | convertImage(charBufferNumber=FINGERPRINT_CHARBUFFER1)
```

Converts the image in image buffer to characteristics and stores it in specified char buffer.

**Arguments**:

- `charBufferNumber` _int_ - The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.


**Returns**:

  True if successful or False otherwise.


**Raises**:

- `ValueError` - if passed char buffer is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.createTemplate"></a>
#### createTemplate

```python
 | createTemplate()
```

Combines the characteristics which are stored in char buffer 1 and char buffer 2 into one template.
The created template will be stored again in char buffer 1 and char buffer 2 as the same.

**Returns**:

  True if successful or False otherwise.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.storeTemplate"></a>
#### storeTemplate

```python
 | storeTemplate(positionNumber=-1, charBufferNumber=FINGERPRINT_CHARBUFFER1)
```

Stores a template from the specified char buffer at the given position.

**Arguments**:

- `positionNumber` _int_ - The position
- `charBufferNumber` _int_ - The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.


**Returns**:

  The position number (int) of the stored template.


**Raises**:

- `ValueError` - if passed position or char buffer is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.searchTemplate"></a>
#### searchTemplate

```python
 | searchTemplate(charBufferNumber=FINGERPRINT_CHARBUFFER1, positionStart=0, count=-1)
```

Searches inside the database for the characteristics in char buffer.

**Arguments**:

- `charBufferNumber` _int_ - The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.
- `positionStart` _int_ - The position to start the search
- `count` _int_ - The number of templates


**Returns**:

  A tuple that contain the following information:
- `0` - integer(2 bytes) The position number of found template.
- `1` - integer(2 bytes) The accuracy score of found template.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.loadTemplate"></a>
#### loadTemplate

```python
 | loadTemplate(positionNumber, charBufferNumber=FINGERPRINT_CHARBUFFER1)
```

Loads an existing template specified by position number to specified char buffer.

**Arguments**:

- `positionNumber` _int_ - The position
- `charBufferNumber` _int_ - The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.


**Returns**:

  True if successful or False otherwise.


**Raises**:

- `ValueError` - if passed position or char buffer is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.deleteTemplate"></a>
#### deleteTemplate

```python
 | deleteTemplate(positionNumber, count=1)
```

Deletes templates from fingerprint database. Per default one.

**Arguments**:

- `positionNumber` _int_ - The position
- `count` _int_ - The number of templates to be deleted.


**Returns**:

  True if successful or False otherwise.


**Raises**:

- `ValueError` - if passed position or count is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.clearDatabase"></a>
#### clearDatabase

```python
 | clearDatabase()
```

Deletes all templates from the fingeprint database.

**Returns**:

  True if successful or False otherwise.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.compareCharacteristics"></a>
#### compareCharacteristics

```python
 | compareCharacteristics()
```

Compare the finger characteristics of char buffer 1 with char buffer 2 and returns the accuracy score.

**Returns**:

  The accuracy score (int). 0 means fingers are not the same.


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.uploadCharacteristics"></a>
#### uploadCharacteristics

```python
 | uploadCharacteristics(charBufferNumber=FINGERPRINT_CHARBUFFER1, characteristicsData=[0])
```

Uploads finger characteristics to specified char buffer.

Author:
David Gilson <davgilson@live.fr>

**Arguments**:

- `charBufferNumber` _int_ - The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.
- `characteristicsData` _list_ - The characteristics


**Returns**:

  True if everything is right.


**Raises**:

- `ValueError` - if passed char buffer or characteristics are invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.generateRandomNumber"></a>
#### generateRandomNumber

```python
 | generateRandomNumber()
```

Generates a random 32-bit decimal number.

Author:
Philipp Meisberger <team@pm-codeworks.de>

**Returns**:

  The generated random number (int).


**Raises**:

- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.downloadCharacteristics"></a>
#### downloadCharacteristics

```python
 | downloadCharacteristics(charBufferNumber=FINGERPRINT_CHARBUFFER1)
```

Downloads the finger characteristics from the specified char buffer.

**Arguments**:

- `charBufferNumber` _int_ - The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.
- `characteristicsData` _list_ - The characteristics


**Returns**:

  The characteristics (list).


**Raises**:

- `ValueError` - if passed char buffer is invalid
- `Exception` - if any error occurs

<a name=".pyfingerprint.PyFingerprint.softReset"></a>
#### softReset

```python
 | softReset()
```

Soft reset the sensor.

Author:
    Chris Borrill <chris.borrill@gmail.com>

<a name=".pyfingerprint.PyFingerprint.checkSensor"></a>
#### checkSensor

```python
 | checkSensor()
```

Check the sensor is in a working state.

Author:
Chris Borrill <chris.borrill@gmail.com>

**Returns**:

  True if the sensor is working correctly.

<a name=".pyfingerprint.PyFingerprint.handshake"></a>
#### handshake

```python
 | handshake()
```

Hand sake with the sensor.

Author:
Chris Borrill <chris.borrill@gmail.com>

**Returns**:

  True if the sensor is working normally.

<a name=".pyfingerprint.PyFingerprint.cancelInstruction"></a>
#### cancelInstruction

```python
 | cancelInstruction()
```

Cancel last intruction to the sensor.

Author:
    Chris Borrill <chris.borrill@gmail.com>

<a name=".pyfingerprint.PyFingerprint.ledOn"></a>
#### ledOn

```python
 | ledOn(colour=FINGERPRINT_LED_RED, control=FINGERPRINT_LED_BREATHING, flashSpeed=0x7D, flashCount=0x00)
```

Turn on sensor LED.

Author:
Chris Borrill <chris.borrill@gmail.com>

**Arguments**:

- `colour` - one of FINGERPRINT_LED_RED (default), FINGERPRINT_LED_BLUE,
  FINGERPRINT_LED_PURPLE
- `control` - one of FINGERPRINT_LED_BREATHING (default),
  FINGERPRINT_LED_BLUE, FINGERPRINT_LED_PURPLE
  FINGERPRINT_LED_CONTINUOUS, FINGERPRINT_LED_OFF,
  FINGERPRINT_LED_GRADUAL_ON, FINGERPRINT_LED_GRADUAL_OFF
- `flashSpeed` - 0 (fast) to 255 (slow) (default 125)
- `flashCount` - 0 (infinite) to 255 (default 0)


**Raises**:

- `Exception` - if an error occured

<a name=".pyfingerprint.PyFingerprint.ledOff"></a>
#### ledOff

```python
 | ledOff()
```

Turn off sensor LED.

Author:
Chris Borrill <chris.borrill@gmail.com>

**Raises**:

- `Exception` - if an error occured
