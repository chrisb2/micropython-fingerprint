"""
PyFingerprint
Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.

"""

import ustruct
from micropython import const


## Baotou start byte
FINGERPRINT_STARTCODE = const(0xEF01)

## Packet identification
##

FINGERPRINT_COMMANDPACKET = const(0x01)

FINGERPRINT_ACKPACKET = const(0x07)
FINGERPRINT_DATAPACKET = const(0x02)
FINGERPRINT_ENDDATAPACKET = const(0x08)

## Instruction codes
##

FINGERPRINT_VERIFYPASSWORD = const(0x13)
FINGERPRINT_SETPASSWORD = const(0x12)
FINGERPRINT_SETADDRESS = const(0x15)
FINGERPRINT_SETSYSTEMPARAMETER = const(0x0E)
FINGERPRINT_GETSYSTEMPARAMETERS = const(0x0F)
FINGERPRINT_TEMPLATEINDEX = const(0x1F)
FINGERPRINT_TEMPLATECOUNT = const(0x1D)
FINGERPRINT_LED_CONFIG = const(0x35)

FINGERPRINT_READIMAGE = const(0x01)

## Note: The documentation mean upload to host computer.
FINGERPRINT_DOWNLOADIMAGE = const(0x0A)

FINGERPRINT_CONVERTIMAGE = const(0x02)

FINGERPRINT_CREATETEMPLATE = const(0x05)
FINGERPRINT_STORETEMPLATE = const(0x06)
FINGERPRINT_SEARCHTEMPLATE = const(0x04)
FINGERPRINT_LOADTEMPLATE = const(0x07)
FINGERPRINT_DELETETEMPLATE = const(0x0C)

FINGERPRINT_CLEARDATABASE = const(0x0D)
FINGERPRINT_GENERATERANDOMNUMBER = const(0x14)
FINGERPRINT_COMPARECHARACTERISTICS = const(0x03)

## Note: The documentation mean download from host computer.
FINGERPRINT_UPLOADCHARACTERISTICS = const(0x09)

## Note: The documentation mean upload to host computer.
FINGERPRINT_DOWNLOADCHARACTERISTICS = const(0x08)

FINGERPRINT_SOFT_RESET = const(0x3D)
FINGERPRINT_CANCEL_INSTRUCTION = const(0x30)
FINGERPRINT_CHECK_SENSOR = const(0x36)
FINGERPRINT_HANDSHAKE = const(0x40)

## Parameters of setSystemParameter()
##

FINGERPRINT_SETSYSTEMPARAMETER_BAUDRATE = const(4)
"""Set the baud rate."""
FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL = const(5)
"""Set the security level."""
FINGERPRINT_SETSYSTEMPARAMETER_PACKAGE_SIZE = const(6)
"""Set the package size."""

## Parameters of ledOn()
##

FINGERPRINT_LED_BREATHING = const(0x01)
"""Breathing LED."""
FINGERPRINT_LED_FLASHING = const(0x02)
"""Flashing LED."""
FINGERPRINT_LED_CONTINUOUS = const(0x03)
"""Continuous LED."""
FINGERPRINT_LED_OFF = const(0x04)
"""LED off."""
FINGERPRINT_LED_GRADUAL_ON = const(0x05)
"""Turn LED on gradually."""
FINGERPRINT_LED_GRADUAL_OFF = const(0x06)
"""Turn LED off gradually."""

FINGERPRINT_LED_RED = const(0x01)
"""Red LED."""
FINGERPRINT_LED_BLUE = const(0x02)
"""Blue LED."""
FINGERPRINT_LED_PURPLE = const(0x03)
"""Purple LED."""

## Packet reply confirmations
##

FINGERPRINT_OK = const(0x00)
FINGERPRINT_ERROR_COMMUNICATION = const(0x01)

FINGERPRINT_ERROR_WRONGPASSWORD = const(0x13)

FINGERPRINT_ERROR_INVALIDREGISTER = const(0x1A)

FINGERPRINT_ERROR_NOFINGER = const(0x02)
FINGERPRINT_ERROR_READIMAGE = const(0x03)

FINGERPRINT_ERROR_MESSYIMAGE = const(0x06)
FINGERPRINT_ERROR_FEWFEATUREPOINTS = const(0x07)
FINGERPRINT_ERROR_INVALIDIMAGE = const(0x15)

FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH = const(0x0A)

FINGERPRINT_ERROR_INVALIDPOSITION = const(0x0B)
FINGERPRINT_ERROR_FLASH = const(0x18)

FINGERPRINT_ERROR_NOTEMPLATEFOUND = const(0x09)

FINGERPRINT_ERROR_LOADTEMPLATE = const(0x0C)

FINGERPRINT_ERROR_DELETETEMPLATE = const(0x10)

FINGERPRINT_ERROR_CLEARDATABASE = const(0x11)

FINGERPRINT_ERROR_NOTMATCHING = const(0x08)

FINGERPRINT_ERROR_DOWNLOADIMAGE = const(0x0F)
FINGERPRINT_ERROR_DOWNLOADCHARACTERISTICS = const(0x0D)

## Unknown error codes
##

FINGERPRINT_ADDRCODE = const(0x20)
FINGERPRINT_PASSVERIFY = const(0x21)

FINGERPRINT_PACKETRESPONSEFAIL = const(0x0E)

FINGERPRINT_ERROR_TIMEOUT = const(0xFF)
FINGERPRINT_ERROR_BADPACKET = const(0xFE)

## Char buffers
##

FINGERPRINT_CHARBUFFER1 = const(0x01)
"""
Char buffer 1
"""

FINGERPRINT_CHARBUFFER2 = const(0x02)
"""
Char buffer 2
"""

class PyFingerprint(object):
    """
    Manages ZhianTec fingerprint sensors.

    """
    __address = None
    __password = None
    __serial = None

    def __init__(self, uart, address=0xFFFFFFFF, password=0x00000000):
        """
        Constructor.

        Arguments:
            uart: Instance of machine.UART. The baud rate set in the UART
            instance MUST be a multiple of 9600. Passing in a UART instance
            enables different flavors of MicroPython to be supported.
            address (int): The sensor address
            password (int): The sensor password

        Raises:
            ValueError: if address or password are invalid
        """
        if ( address < 0x00000000 or address > 0xFFFFFFFF ):
            raise ValueError('The given address is invalid!')

        if ( password < 0x00000000 or password > 0xFFFFFFFF ):
            raise ValueError('The given password is invalid!')

        self.__address = address
        self.__password = password

        # Initialize PySerial connection
        self.__serial = uart

    def __del__(self):
        """Destructor."""
        # Close connection if still established
        self.__serial.deinit()

    def __rightShift(self, n, x):
        """
        Performs a right-shift.

        Arguments:
            n (int): The number
            x (int): The amount of bits to shift

        Returns:
            The shifted number (int)
        """

        return (n >> x & 0xFF)

    def __leftShift(self, n, x):
        """
        Performs a left-shift.

        Arguments:
            n (int): The number
            x (int): The amount of bits to shift

        Returns:
            The shifted number (int)
        """

        return (n << x)

    def __bitAtPosition(self, n, p):
        """
        Gets the bit at the specified position.

        Arguments:
            n (int): The number
            x (int): The position

        Returns:
            The bit number (int)
        """

        ## A bitshift 2 ^ p
        twoP = 1 << p

        ## Binary AND composition (on both positions must be a 1)
        ## This can only happen at position p
        result = n & twoP
        return int(result > 0)

    def __byteToString(self, byte):
        """
        Converts a byte to string.

        Arguments:
            byte (int): The byte

        Returns:
            The string (str)
        """

        return ustruct.pack('@B', byte)

    def __stringToByte(self, string):
        """
        Convert one "string" byte (like '0xFF') to real integer byte (0xFF).

        Arguments:
            string (str): The string

        Returns:
            The byte (int)
        """

        return ustruct.unpack('@B', string)[0]

    def __writePacket(self, packetType, packetPayload):
        """
        Sends a packet to the sensor.

        Arguments:
            packetType (int): The packet type (either `FINGERPRINT_COMMANDPACKET`, `FINGERPRINT_DATAPACKET` or `FINGERPRINT_ENDDATAPACKET`)
            packetPayload (tuple): The payload
        """

        ## Write header (one byte at once)
        self.__serial.write(self.__byteToString(self.__rightShift(FINGERPRINT_STARTCODE, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(FINGERPRINT_STARTCODE, 0)))

        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 24)))
        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 16)))
        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 0)))

        self.__serial.write(self.__byteToString(packetType))

        ## The packet length = package payload (n bytes) + checksum (2 bytes)
        packetLength = len(packetPayload) + 2

        self.__serial.write(self.__byteToString(self.__rightShift(packetLength, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(packetLength, 0)))

        ## The packet checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
        packetChecksum = packetType + self.__rightShift(packetLength, 8) + self.__rightShift(packetLength, 0)

        ## Write payload
        for i in range(0, len(packetPayload)):
            self.__serial.write(self.__byteToString(packetPayload[i]))
            packetChecksum += packetPayload[i]

        ## Write checksum (2 bytes)
        self.__serial.write(self.__byteToString(self.__rightShift(packetChecksum, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(packetChecksum, 0)))

    def __readPacket(self):
        """
        Receives a packet from the sensor.

        Returns:
            A tuple that contain the following information:
            0: integer(1 byte) The packet type.
            1: integer(n bytes) The packet payload.

        Raises:
            Exception: if checksum is wrong
        """

        receivedPacketData = []
        i = 0

        while ( True ):

            # Read one byte
            receivedFragment = self.__serial.read(1)

            if (receivedFragment is not None and len(receivedFragment) != 0):
                receivedFragment = self.__stringToByte(receivedFragment)
                ## print 'Received packet fragment = ' + hex(receivedFragment
            else:
                continue

            ## Insert byte if packet seems valid
            receivedPacketData.insert(i, receivedFragment)
            i += 1

            ## Packet could be complete (the minimal packet size is 12 bytes)
            if ( i >= 12 ):

                ## Check the packet header
                if ( receivedPacketData[0] != self.__rightShift(FINGERPRINT_STARTCODE, 8) or receivedPacketData[1] != self.__rightShift(FINGERPRINT_STARTCODE, 0) ):
                    raise Exception('The received packet do not begin with a valid header!')

                ## Calculate packet payload length (combine the 2 length bytes)
                packetPayloadLength = self.__leftShift(receivedPacketData[7], 8)
                packetPayloadLength = packetPayloadLength | self.__leftShift(receivedPacketData[8], 0)

                ## Check if the packet is still fully received
                ## Condition: index counter < packet payload length + packet frame
                if ( i < packetPayloadLength + 9 ):
                    continue

                ## At this point the packet should be fully received

                packetType = receivedPacketData[6]

                ## Calculate checksum:
                ## checksum = packet type (1 byte) + packet length (2 bytes) + packet payload (n bytes)
                packetChecksum = packetType + receivedPacketData[7] + receivedPacketData[8]

                packetPayload = []

                ## Collect package payload (ignore the last 2 checksum bytes)
                for j in range(9, 9 + packetPayloadLength - 2):
                    packetPayload.append(receivedPacketData[j])
                    packetChecksum += receivedPacketData[j]

                ## Calculate full checksum of the 2 separate checksum bytes
                receivedChecksum = self.__leftShift(receivedPacketData[i - 2], 8)
                receivedChecksum = receivedChecksum | self.__leftShift(receivedPacketData[i - 1], 0)

                if ( receivedChecksum != packetChecksum ):
                    raise Exception('The received packet is corrupted (the checksum is wrong)!')

                return (packetType, packetPayload)

    def verifyPassword(self):
        """
        Verifies password of the sensor.

        Returns:
            True if password is correct or False otherwise.

        Raises:
            Exception: if an error occured
        """

        packetPayload = (
            FINGERPRINT_VERIFYPASSWORD,
            self.__rightShift(self.__password, 24),
            self.__rightShift(self.__password, 16),
            self.__rightShift(self.__password, 8),
            self.__rightShift(self.__password, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Sensor password is correct
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ADDRCODE ):
            raise Exception('The address is wrong')

        ## DEBUG: Sensor password is wrong
        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_WRONGPASSWORD ):
            return False

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def setPassword(self, newPassword):
        """
        Sets the password of the sensor.

        Arguments:
            newPassword (int): The new password to use.

        Returns:
            True if password was set correctly or False otherwise.

        Raises:
            Exception: if an error occured
        """

        ## Validate the password (maximum 4 bytes)
        if ( newPassword < 0x00000000 or newPassword > 0xFFFFFFFF ):
            raise ValueError('The given password is invalid!')

        packetPayload = (
            FINGERPRINT_SETPASSWORD,
            self.__rightShift(newPassword, 24),
            self.__rightShift(newPassword, 16),
            self.__rightShift(newPassword, 8),
            self.__rightShift(newPassword, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Password set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            self.__password = newPassword
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def setAddress(self, newAddress):
        """
        Sets the sensor address.

        Arguments:
            newAddress (int): The new address to use.

        Returns:
            True if address was set correctly or False otherwise.

        Raises:
            Exception: if any error occurs
        """

        ## Validate the address (maximum 4 bytes)
        if ( newAddress < 0x00000000 or newAddress > 0xFFFFFFFF ):
            raise ValueError('The given address is invalid!')

        packetPayload = (
            FINGERPRINT_SETADDRESS,
            self.__rightShift(newAddress, 24),
            self.__rightShift(newAddress, 16),
            self.__rightShift(newAddress, 8),
            self.__rightShift(newAddress, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Address set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            self.__address = newAddress
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def setSystemParameter(self, parameterNumber, parameterValue):
        """
        Set a system parameter of the sensor.

        Arguments:
            parameterNumber (int): The parameter number. Use one of `FINGERPRINT_SETSYSTEMPARAMETER_*` constants.
            parameterValue (int): The value

        Returns:
            True if successful or False otherwise.

        Raises:
            ValueError: if any passed parameter is invalid
            Exception: if any error occurs
        """

        ## Validate the baud rate parameter
        if ( parameterNumber == FINGERPRINT_SETSYSTEMPARAMETER_BAUDRATE ):

            if ( parameterValue < 1 or parameterValue > 12 ):
                raise ValueError('The given baud rate parameter is invalid!')

        ## Validate the security level parameter
        elif ( parameterNumber == FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL ):

            if ( parameterValue < 1 or parameterValue > 5 ):
                raise ValueError('The given security level parameter is invalid!')

        ## Validate the package length parameter
        elif ( parameterNumber == FINGERPRINT_SETSYSTEMPARAMETER_PACKAGE_SIZE ):

            if ( parameterValue < 0 or parameterValue > 3 ):
                raise ValueError('The given package length parameter is invalid!')

        ## The parameter number is not valid
        else:
            raise ValueError('The given parameter number is invalid!')

        packetPayload = (
            FINGERPRINT_SETSYSTEMPARAMETER,
            parameterNumber,
            parameterValue,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Parameter set was successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDREGISTER ):
            raise Exception('Invalid register number')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def setBaudRate(self, baudRate):
        """
        Sets the baud rate.

        Arguments:
            baudRate (int): The baud rate

        Raises:
            ValueError: if passed baud rate is no multiple of 9600
            Exception: if any error occurs
        """

        if (baudRate % 9600 != 0):
            raise ValueError("Invalid baud rate")

        self.setSystemParameter(FINGERPRINT_SETSYSTEMPARAMETER_BAUDRATE, baudRate // 9600)

    def setSecurityLevel(self, securityLevel):
        """
        Sets the security level of the sensor.

        Arguments:
            securityLevel (int): Value between 1 and 5 where 1 is lowest and 5 highest.

        Raises:
            Exception: if any error occurs
        """

        self.setSystemParameter(FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL, securityLevel)

    def setMaxPacketSize(self, packetSize):
        """
        Sets the maximum packet size of sensor.

        Arguments:
            packetSize (int): 32, 64, 128 and 256 are supported.

        Raises:
            ValueError: if passed packet size is invalid
            Exception: if any error occurs
        """

        try:
            packetSizes = {32: 0, 64: 1, 128: 2, 256: 3}
            packetMaxSizeType = packetSizes[packetSize]

        except KeyError:
            raise ValueError("Invalid packet size")

        self.setSystemParameter(FINGERPRINT_SETSYSTEMPARAMETER_PACKAGE_SIZE, packetMaxSizeType)

    def getSystemParameters(self):
        """
        Gets all available system information of the sensor.

        Returns:
            A tuple that contains the following information:
            0: integer(2 bytes) The status register.
            1: integer(2 bytes) The system id.
            2: integer(2 bytes) The storage capacity.
            3: integer(2 bytes) The security level.
            4: integer(4 bytes) The sensor address.
            5: integer(2 bytes) The packet length.
            6: integer(2 bytes) The baud rate.

        Raises:
            Exception: if any error occurs
        """

        packetPayload = (
            FINGERPRINT_GETSYSTEMPARAMETERS,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Read successfully
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

            statusRegister     = self.__leftShift(receivedPacketPayload[1], 8) | self.__leftShift(receivedPacketPayload[2], 0)
            systemID           = self.__leftShift(receivedPacketPayload[3], 8) | self.__leftShift(receivedPacketPayload[4], 0)
            storageCapacity    = self.__leftShift(receivedPacketPayload[5], 8) | self.__leftShift(receivedPacketPayload[6], 0)
            securityLevel      = self.__leftShift(receivedPacketPayload[7], 8) | self.__leftShift(receivedPacketPayload[8], 0)
            deviceAddress      = ((receivedPacketPayload[9] << 8 | receivedPacketPayload[10]) << 8 | receivedPacketPayload[11]) << 8 | receivedPacketPayload[12] ## TODO
            packetLength       = self.__leftShift(receivedPacketPayload[13], 8) | self.__leftShift(receivedPacketPayload[14], 0)
            baudRate           = self.__leftShift(receivedPacketPayload[15], 8) | self.__leftShift(receivedPacketPayload[16], 0)

            return (statusRegister, systemID, storageCapacity, securityLevel, deviceAddress, packetLength, baudRate)

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def getStorageCapacity(self):
        """
        Gets the sensor storage capacity.

        Returns:
            The storage capacity (int).

        Raises:
            Exception: if any error occurs
        """

        return self.getSystemParameters()[2]

    def getSecurityLevel(self):
        """
        Gets the security level of the sensor.

        Returns:
            The security level (int).

        Raises:
            Exception: if any error occurs
        """

        return self.getSystemParameters()[3]

    def getMaxPacketSize(self):
        """
        Gets the maximum allowed size of a single packet.

        Returns:
            Return the max size (int).

        Raises:
            ValueError: if packet size is invalid
            Exception: if any error occurs
        """

        packetMaxSizeType = self.getSystemParameters()[5]

        try:
            packetSizes = [32, 64, 128, 256]
            packetSize = packetSizes[packetMaxSizeType]

        except KeyError:
            raise ValueError("Invalid packet size")

        return packetSize

    def getBaudRate(self):
        """
        Gets the baud rate.

        Returns:
            The baud rate (int).

        Raises:
            Exception: if any error occurs
        """

        return self.getSystemParameters()[6] * 9600

    def getTemplateIndex(self, page):
        """
        Gets a list of the template positions with usage indicator.

        Arguments:
            page (int): The page (value between 0 and 3).

        Returns:
            The list.

        Raises:
            ValueError: if passed page is invalid
            Exception: if any error occurs
        """

        if ( page < 0 or page > 3 ):
            raise ValueError('The given index page is invalid!')

        packetPayload = (
            FINGERPRINT_TEMPLATEINDEX,
            page,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Read index table successfully
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

            templateIndex = []

            ## Contain the table page bytes (skip the first status byte)
            pageElements = receivedPacketPayload[1:]

            for pageElement in pageElements:
                ## Test every bit (bit = template position is used indicator) of a table page element
                for p in range(0, 7 + 1):
                    positionIsUsed = (self.__bitAtPosition(pageElement, p) == 1)
                    templateIndex.append(positionIsUsed)

            return templateIndex

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def getTemplateCount(self):
        """
        Gets the number of stored templates.

        Returns:
            The template count (int).

        Raises:
            Exception: if any error occurs
        """

        packetPayload = (
            FINGERPRINT_TEMPLATECOUNT,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Read successfully
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            templateCount = self.__leftShift(receivedPacketPayload[1], 8)
            templateCount = templateCount | self.__leftShift(receivedPacketPayload[2], 0)
            return templateCount

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def readImage(self):
        """
        Reads the image of a finger and stores it in image buffer.

        Returns:
            True if image was read successfully or False otherwise.

        Raises:
            Exception: if any error occurs
        """

        packetPayload = (
            FINGERPRINT_READIMAGE,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Image read successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        ## DEBUG: No finger found
        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_NOFINGER ):
            return False

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_READIMAGE ):
            raise Exception('Could not read image')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def convertImage(self, charBufferNumber = FINGERPRINT_CHARBUFFER1):
        """
        Converts the image in image buffer to characteristics and stores it in specified char buffer.

        Arguments:
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Returns:
            True if successful or False otherwise.

        Raises:
            ValueError: if passed char buffer is invalid
            Exception: if any error occurs
        """

        if ( charBufferNumber != FINGERPRINT_CHARBUFFER1 and charBufferNumber != FINGERPRINT_CHARBUFFER2 ):
            raise ValueError('The given char buffer number is invalid!')

        packetPayload = (
            FINGERPRINT_CONVERTIMAGE,
            charBufferNumber,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Image converted
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_MESSYIMAGE ):
            raise Exception('The image is too messy')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_FEWFEATUREPOINTS ):
            raise Exception('The image contains too few feature points')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDIMAGE ):
            raise Exception('The image is invalid')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def createTemplate(self):
        """
        Combines the characteristics which are stored in char buffer 1 and char buffer 2 into one template.
        The created template will be stored again in char buffer 1 and char buffer 2 as the same.

        Returns:
            True if successful or False otherwise.

        Raises:
            Exception: if any error occurs
        """

        packetPayload = (
            FINGERPRINT_CREATETEMPLATE,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template created successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        ## DEBUG: The characteristics not matching
        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH ):
            return False

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def storeTemplate(self, positionNumber = -1, charBufferNumber = FINGERPRINT_CHARBUFFER1):
        """
        Stores a template from the specified char buffer at the given position.

        Arguments:
            positionNumber (int): The position
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Returns:
            The position number (int) of the stored template.

        Raises:
            ValueError: if passed position or char buffer is invalid
            Exception: if any error occurs
        """

        ## Find a free index
        if ( positionNumber == -1 ):
            for page in range(0, 4):
                ## Free index found?
                if ( positionNumber >= 0 ):
                    break

                templateIndex = self.getTemplateIndex(page)

                for i in range(0, len(templateIndex)):
                    ## Index not used?
                    if ( templateIndex[i] is False ):
                        positionNumber = (len(templateIndex) * page) + i
                        break

        if ( positionNumber < 0x0000 or positionNumber >= self.getStorageCapacity() ):
            raise ValueError('The given position number is invalid!')

        if ( charBufferNumber != FINGERPRINT_CHARBUFFER1 and charBufferNumber != FINGERPRINT_CHARBUFFER2 ):
            raise ValueError('The given char buffer number is invalid!')

        packetPayload = (
            FINGERPRINT_STORETEMPLATE,
            charBufferNumber,
            self.__rightShift(positionNumber, 8),
            self.__rightShift(positionNumber, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template stored successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return positionNumber

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDPOSITION ):
            raise Exception('Could not store template in that position')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_FLASH ):
            raise Exception('Error writing to flash')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def searchTemplate(self, charBufferNumber = FINGERPRINT_CHARBUFFER1, positionStart = 0, count = -1):
        """
        Searches inside the database for the characteristics in char buffer.

        Arguments:
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.
            positionStart (int): The position to start the search
            count (int): The number of templates

        Returns:
            A tuple that contain the following information:
            0: integer(2 bytes) The position number of found template.
            1: integer(2 bytes) The accuracy score of found template.

        Raises:
            Exception: if any error occurs
        """

        if ( charBufferNumber != FINGERPRINT_CHARBUFFER1 and charBufferNumber != FINGERPRINT_CHARBUFFER2 ):
            raise ValueError('The given charbuffer number is invalid!')

        if ( count > 0 ):
            templatesCount = count
        else:
            templatesCount = self.getStorageCapacity()

        packetPayload = (
            FINGERPRINT_SEARCHTEMPLATE,
            charBufferNumber,
            self.__rightShift(positionStart, 8),
            self.__rightShift(positionStart, 0),
            self.__rightShift(templatesCount, 8),
            self.__rightShift(templatesCount, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Found template
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):

            positionNumber = self.__leftShift(receivedPacketPayload[1], 8)
            positionNumber = positionNumber | self.__leftShift(receivedPacketPayload[2], 0)

            accuracyScore = self.__leftShift(receivedPacketPayload[3], 8)
            accuracyScore = accuracyScore | self.__leftShift(receivedPacketPayload[4], 0)

            return (positionNumber, accuracyScore)

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        ## DEBUG: Did not found a matching template
        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_NOTEMPLATEFOUND ):
            return (-1, -1)

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def loadTemplate(self, positionNumber, charBufferNumber = FINGERPRINT_CHARBUFFER1):
        """
        Loads an existing template specified by position number to specified char buffer.

        Arguments:
            positionNumber (int): The position
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Returns:
            True if successful or False otherwise.

        Raises:
            ValueError: if passed position or char buffer is invalid
            Exception: if any error occurs
        """

        if ( positionNumber < 0x0000 or positionNumber >= self.getStorageCapacity() ):
            raise ValueError('The given position number is invalid!')

        if ( charBufferNumber != FINGERPRINT_CHARBUFFER1 and charBufferNumber != FINGERPRINT_CHARBUFFER2 ):
            raise ValueError('The given char buffer number is invalid!')

        packetPayload = (
            FINGERPRINT_LOADTEMPLATE,
            charBufferNumber,
            self.__rightShift(positionNumber, 8),
            self.__rightShift(positionNumber, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template loaded successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_LOADTEMPLATE ):
            raise Exception('The template could not be read')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDPOSITION ):
            raise Exception('Could not load template from that position')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def deleteTemplate(self, positionNumber, count = 1):
        """
        Deletes templates from fingerprint database. Per default one.

        Arguments:
            positionNumber (int): The position
            count (int): The number of templates to be deleted.

        Returns:
            True if successful or False otherwise.

        Raises:
            ValueError: if passed position or count is invalid
            Exception: if any error occurs
        """

        capacity = self.getStorageCapacity()

        if ( positionNumber < 0x0000 or positionNumber >= capacity ):
            raise ValueError('The given position number is invalid!')

        if ( count < 0x0000 or count > capacity - positionNumber ):
            raise ValueError('The given count is invalid!')

        packetPayload = (
            FINGERPRINT_DELETETEMPLATE,
            self.__rightShift(positionNumber, 8),
            self.__rightShift(positionNumber, 0),
            self.__rightShift(count, 8),
            self.__rightShift(count, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Template deleted successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_INVALIDPOSITION ):
            raise Exception('Invalid position')

        ## DEBUG: Could not delete template
        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_DELETETEMPLATE ):
            return False

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def clearDatabase(self):
        """
        Deletes all templates from the fingeprint database.

        Returns:
            True if successful or False otherwise.

        Raises:
            Exception: if any error occurs
        """

        packetPayload = (
            FINGERPRINT_CLEARDATABASE,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Database cleared successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            return True

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        ## DEBUG: Could not clear database
        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_CLEARDATABASE ):
            return False

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def compareCharacteristics(self):
        """
        Compare the finger characteristics of char buffer 1 with char buffer 2 and returns the accuracy score.

        Returns:
            The accuracy score (int). 0 means fingers are not the same.

        Raises:
            Exception: if any error occurs
        """

        packetPayload = (
            FINGERPRINT_COMPARECHARACTERISTICS,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: Comparison successful
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            accuracyScore = self.__leftShift(receivedPacketPayload[1], 8)
            accuracyScore = accuracyScore | self.__leftShift(receivedPacketPayload[2], 0)
            return accuracyScore

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        ## DEBUG: The characteristics do not matching
        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_NOTMATCHING ):
            return 0

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

    def uploadCharacteristics(self, charBufferNumber = FINGERPRINT_CHARBUFFER1, characteristicsData = [0]):
        """
        Uploads finger characteristics to specified char buffer.

        Author:
            David Gilson <davgilson@live.fr>

        Arguments:
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.
            characteristicsData (list): The characteristics

        Returns:
            True if everything is right.

        Raises:
            ValueError: if passed char buffer or characteristics are invalid
            Exception: if any error occurs
        """

        if ( charBufferNumber != FINGERPRINT_CHARBUFFER1 and charBufferNumber != FINGERPRINT_CHARBUFFER2 ):
            raise ValueError('The given char buffer number is invalid!')

        if ( characteristicsData == [0] ):
            raise ValueError('The characteristics data is required!')

        maxPacketSize = self.getMaxPacketSize()

        ## Upload command

        packetPayload = (
            FINGERPRINT_UPLOADCHARACTERISTICS,
            charBufferNumber
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        ## Get first reply packet
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: The sensor will sent follow-up packets
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            pass

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_PACKETRESPONSEFAIL ):
            raise Exception('Could not upload characteristics')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

        ## Upload data packets
        packetNbr = len(characteristicsData) / maxPacketSize

        if ( packetNbr <= 1 ):
            self.__writePacket(FINGERPRINT_ENDDATAPACKET, characteristicsData)
        else:
            i = 1
            while ( i < packetNbr ):
                lfrom = (i-1) * maxPacketSize
                lto = lfrom + maxPacketSize
                self.__writePacket(FINGERPRINT_DATAPACKET, characteristicsData[lfrom:lto])
                i += 1

            lfrom = (i-1) * maxPacketSize
            lto = lfrom + maxPacketSize
            self.__writePacket(FINGERPRINT_ENDDATAPACKET, characteristicsData[lfrom:lto])

        ## Verify uploaded characteristics
        characterics = self.downloadCharacteristics(charBufferNumber)
        return (characterics == characteristicsData)

    def generateRandomNumber(self):
        """
        Generates a random 32-bit decimal number.

        Author:
            Philipp Meisberger <team@pm-codeworks.de>

        Returns:
            The generated random number (int).

        Raises:
            Exception: if any error occurs
        """
        packetPayload = (
            FINGERPRINT_GENERATERANDOMNUMBER,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            pass

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

        number = 0
        number = number | self.__leftShift(receivedPacketPayload[1], 24)
        number = number | self.__leftShift(receivedPacketPayload[2], 16)
        number = number | self.__leftShift(receivedPacketPayload[3], 8)
        number = number | self.__leftShift(receivedPacketPayload[4], 0)
        return number

    def downloadCharacteristics(self, charBufferNumber = FINGERPRINT_CHARBUFFER1):
        """
        Downloads the finger characteristics from the specified char buffer.

        Arguments:
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.
            characteristicsData (list): The characteristics

        Returns:
            The characteristics (list).

        Raises:
            ValueError: if passed char buffer is invalid
            Exception: if any error occurs
        """

        if ( charBufferNumber != FINGERPRINT_CHARBUFFER1 and charBufferNumber != FINGERPRINT_CHARBUFFER2 ):
            raise ValueError('The given char buffer number is invalid!')

        packetPayload = (
            FINGERPRINT_DOWNLOADCHARACTERISTICS,
            charBufferNumber,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        ## Get first reply packet
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if ( receivedPacketType != FINGERPRINT_ACKPACKET ):
            raise Exception('The received packet is no ack packet!')

        ## DEBUG: The sensor will sent follow-up packets
        if ( receivedPacketPayload[0] == FINGERPRINT_OK ):
            pass

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION ):
            raise Exception('Communication error')

        elif ( receivedPacketPayload[0] == FINGERPRINT_ERROR_DOWNLOADCHARACTERISTICS ):
            raise Exception('Could not download characteristics')

        else:
            raise Exception('Unknown error '+ hex(receivedPacketPayload[0]))

        completePayload = []

        ## Get follow-up data packets until the last data packet is received
        while ( receivedPacketType != FINGERPRINT_ENDDATAPACKET ):

            receivedPacket = self.__readPacket()

            receivedPacketType = receivedPacket[0]
            receivedPacketPayload = receivedPacket[1]

            if ( receivedPacketType != FINGERPRINT_DATAPACKET and receivedPacketType != FINGERPRINT_ENDDATAPACKET ):
                raise Exception('The received packet is no data packet!')

            for i in range(0, len(receivedPacketPayload)):
                completePayload.append(receivedPacketPayload[i])

        return completePayload

    def softReset(self):
        """Soft reset the sensor.

        Author:
            Chris Borrill <chris.borrill@gmail.com>
        """
        packetPayload = (
            FINGERPRINT_SOFT_RESET,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if (receivedPacketType != FINGERPRINT_ACKPACKET):
            raise Exception('The received packet is no ack packet!')

        if (receivedPacketPayload[0] != FINGERPRINT_OK):
            raise Exception('Unknown error ' + hex(receivedPacketPayload[0]))

        # Wait for handshake on reset completion
        while(self.__serial.read(1) != b'U'):
            pass

    def checkSensor(self):
        """Check the sensor is in a working state.

        Author:
            Chris Borrill <chris.borrill@gmail.com>

        Returns:
            True if the sensor is working correctly.
        """
        packetPayload = (
            FINGERPRINT_CHECK_SENSOR,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if (receivedPacketType != FINGERPRINT_ACKPACKET):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload[0] == FINGERPRINT_OK

    def handshake(self):
        """Hand shake with the sensor.

        Author:
            Chris Borrill <chris.borrill@gmail.com>

        Returns:
            True if the sensor is working normally.
        """
        packetPayload = (
            FINGERPRINT_HANDSHAKE,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if (receivedPacketType != FINGERPRINT_ACKPACKET):
            raise Exception('The received packet is no ack packet!')

        return receivedPacketPayload[0] == FINGERPRINT_OK

    def cancelInstruction(self):
        """Cancel last intruction to the sensor.

        Author:
            Chris Borrill <chris.borrill@gmail.com>
        """
        packetPayload = (
            FINGERPRINT_CANCEL_INSTRUCTION,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if (receivedPacketType != FINGERPRINT_ACKPACKET):
            raise Exception('The received packet is no ack packet!')

        if (receivedPacketPayload[0] != FINGERPRINT_OK):
            raise Exception('Unknown error ' + hex(receivedPacketPayload[0]))

    def ledOn(self, colour=FINGERPRINT_LED_RED,
              control=FINGERPRINT_LED_BREATHING,
              flashSpeed=0x7D, flashCount=0x00):
        """
        Turn on sensor LED.

        Author:
            Chris Borrill <chris.borrill@gmail.com>

        Arguments:
            colour: one of FINGERPRINT_LED_RED (default), FINGERPRINT_LED_BLUE,
            FINGERPRINT_LED_PURPLE
            control: one of FINGERPRINT_LED_BREATHING (default),
            FINGERPRINT_LED_BLUE, FINGERPRINT_LED_PURPLE
            FINGERPRINT_LED_CONTINUOUS, FINGERPRINT_LED_OFF,
            FINGERPRINT_LED_GRADUAL_ON, FINGERPRINT_LED_GRADUAL_OFF
            flashSpeed: 0 (fast) to 255 (slow) (default 125)
            flashCount: 0 (infinite) to 255 (default 0)

        Raises:
            Exception: if an error occured
        """
        self.__led(control, colour, flashSpeed, flashCount)

    def ledOff(self):
        """
        Turn off sensor LED.

        Author:
            Chris Borrill <chris.borrill@gmail.com>

        Raises:
            Exception: if an error occured
        """
        self.__led(FINGERPRINT_LED_OFF, 0x00, 0x00, 0x00)

    def __led(self, control, colour, flashSpeed, flashCount):
        packetPayload = (
            FINGERPRINT_LED_CONFIG,
            control,
            flashSpeed,
            colour,
            flashCount
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)
        receivedPacket = self.__readPacket()

        receivedPacketType = receivedPacket[0]
        receivedPacketPayload = receivedPacket[1]

        if (receivedPacketType != FINGERPRINT_ACKPACKET):
            raise Exception('The received packet is no ack packet!')

        if (receivedPacketPayload[0] == FINGERPRINT_OK):
            pass
        elif (receivedPacketPayload[0] == FINGERPRINT_ERROR_COMMUNICATION):
            raise Exception('Communication error')
        else:
            raise Exception('Unknown error ' + hex(receivedPacketPayload[0]))
