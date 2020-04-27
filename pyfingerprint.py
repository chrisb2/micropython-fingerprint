"""
PyFingerprint.

Copyright (C) 2015 Bastian Raschke <bastian.raschke@posteo.de>
All rights reserved.
"""

import ustruct
from micropython import const
import logging


# Start byte
FINGERPRINT_STARTCODE = const(0xEF01)

# Packet identification
FINGERPRINT_COMMANDPACKET = const(0x01)
FINGERPRINT_ACKPACKET = const(0x07)
FINGERPRINT_DATAPACKET = const(0x02)
FINGERPRINT_ENDDATAPACKET = const(0x08)

# Instruction codes
FINGERPRINT_VERIFYPASSWORD = const(0x13)
FINGERPRINT_SETPASSWORD = const(0x12)
FINGERPRINT_SETADDRESS = const(0x15)
FINGERPRINT_SETSYSTEMPARAMETER = const(0x0E)
FINGERPRINT_GETSYSTEMPARAMETERS = const(0x0F)
FINGERPRINT_TEMPLATEINDEX = const(0x1F)
FINGERPRINT_TEMPLATECOUNT = const(0x1D)
FINGERPRINT_LED_CONFIG = const(0x35)
FINGERPRINT_READIMAGE = const(0x01)
# Note: The documentation mean upload to host computer.
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
# Note: The documentation mean download from host computer.
FINGERPRINT_UPLOADCHARACTERISTICS = const(0x09)
# Note: The documentation mean upload to host computer.
FINGERPRINT_DOWNLOADCHARACTERISTICS = const(0x08)
FINGERPRINT_SOFT_RESET = const(0x3D)
FINGERPRINT_CANCEL_INSTRUCTION = const(0x30)
FINGERPRINT_CHECK_SENSOR = const(0x36)
FINGERPRINT_HANDSHAKE = const(0x40)

# Parameters of setSystemParameter()
FINGERPRINT_SETSYSTEMPARAMETER_BAUDRATE = const(4)
"""Set the baud rate."""
FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL = const(5)
"""Set the security level."""
FINGERPRINT_SETSYSTEMPARAMETER_PACKAGE_SIZE = const(6)
"""Set the package size."""

# Parameters of ledOn()
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

# Packet reply confirmations
FINGERPRINT_OK = const(0x00)
FINGERPRINT_ERROR_NOFINGER = const(0x02)
FINGERPRINT_ERROR_NOTMATCHING = const(0x08)
FINGERPRINT_ERROR_NOTEMPLATEFOUND = const(0x09)
FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH = const(0x0A)
FINGERPRINT_ERROR_WRONGPASSWORD = const(0x13)
FINGERPRINT_ERROR_CODES = {
    0x01: "Communication error",
    FINGERPRINT_ERROR_NOFINGER: "No finger on the sensor",
    0x03: "Failed to read finger image",
    0x06: "The image is too messy",
    0x07: "The image contains too few feature points",
    FINGERPRINT_ERROR_NOTMATCHING: "Finger does not match",
    FINGERPRINT_ERROR_NOTEMPLATEFOUND: "No template found",
    FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH: "Characteristic mismatch",
    0x0B: "Could not load template from that position",
    0x0C: "Error reading template from library",
    0x0D: "Error downloading template",
    0x0E: "Module cannot received following packages",
    0x0F: "Error downloading image",
    0x10: "Error deleting template",
    0x11: "Error deleting database",
    FINGERPRINT_ERROR_WRONGPASSWORD: "Wrong password",
    0x15: "Invalid image",
    0x18: "Flash error",
    0x19: "No definition error",
    0x1A: "Invalid register",
    0x1B: "Incorrect register configuration",
    0x1C: "Wrong notepad page number",
    0x1D: "Failed to operate the communication port",
    # Undocumented
    0x20: "The address is wrong",
}

# Char buffers
FINGERPRINT_CHARBUFFER1 = const(0x01)
"""
Char buffer 1
"""
FINGERPRINT_CHARBUFFER2 = const(0x02)
"""
Char buffer 2
"""


class PyFingerprint(object):
    """Manage ZhianTec fingerprint sensors."""

    __address = None
    __password = None
    __serial = None

    def __init__(self, uart, address=0xFFFFFFFF, password=0x00000000,
                 log_level=logging.ERROR):
        """
        Constructor.

        Arguments:
            uart: Instance of machine.UART. The baud rate set in the UART
            instance MUST be a multiple of 9600. Passing in a UART instance
            enables different flavors of MicroPython to be supported.
            address (int): The sensor address
            password (int): The sensor password
            log_level: control logging of set/recieved data.
            Set to logging.DEBUG to see output.

        Raises:
            ValueError: if address or password are invalid
        """
        if (address < 0x00000000 or address > 0xFFFFFFFF):
            raise ValueError('The given address is invalid!')

        if (password < 0x00000000 or password > 0xFFFFFFFF):
            raise ValueError('The given password is invalid!')

        # TODO - handle root logger scenario
        logging.basicConfig(level=log_level)
        self._log = logging.getLogger("pyfingerprint")

        self.__address = address
        self.__password = password
        self.__serial = uart

        # TODO  - use getMaxPackageSize?
        self.__payloadBuffer = bytearray(32)

    def __del__(self):
        """Destructor."""
        # Close connection if still established
        self.__serial.deinit()

    def __rightShift(self, n, x):
        """
        Perform a right-shift.

        Arguments:
            n (int): The number
            x (int): The amount of bits to shift

        Returns:
            The shifted number (int)
        """
        return (n >> x & 0xFF)

    def __leftShift(self, n, x):
        """
        Perform a left-shift.

        Arguments:
            n (int): The number
            x (int): The amount of bits to shift

        Returns:
            The shifted number (int)
        """
        return (n << x)

    def __bitAtPosition(self, n, p):
        """
        Get the bit at the specified position.

        Arguments:
            n (int): The number
            x (int): The position

        Returns:
            The bit number (int)
        """
        # A bitshift 2 ^ p
        twoP = 1 << p

        # Binary AND composition (on both positions must be a 1)
        # This can only happen at position p
        result = n & twoP
        return int(result > 0)

    def __byteToString(self, byte):
        """
        Convert a byte to string.

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
        Send a packet to the sensor.

        Arguments:
            packetType (int): The packet type (either `FINGERPRINT_COMMANDPACKET`, `FINGERPRINT_DATAPACKET` or `FINGERPRINT_ENDDATAPACKET`)
            packetPayload (tuple): The payload
        """
        # Write header (one byte at once)
        self.__serial.write(self.__byteToString(self.__rightShift(FINGERPRINT_STARTCODE, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(FINGERPRINT_STARTCODE, 0)))

        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 24)))
        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 16)))
        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(self.__address, 0)))

        self.__serial.write(self.__byteToString(packetType))

        # The packet length = package payload (n bytes) + checksum (2 bytes)
        packetLength = len(packetPayload) + 2

        self.__serial.write(self.__byteToString(self.__rightShift(packetLength, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(packetLength, 0)))

        # The packet checksum = packet type (1 byte) + packet length (2 bytes) + payload (n bytes)
        packetChecksum = packetType + self.__rightShift(packetLength, 8) + self.__rightShift(packetLength, 0)

        # Write payload
        for i in range(0, len(packetPayload)):
            self.__serial.write(self.__byteToString(packetPayload[i]))
            packetChecksum += packetPayload[i]

        # Write checksum (2 bytes)
        self.__serial.write(self.__byteToString(self.__rightShift(packetChecksum, 8)))
        self.__serial.write(self.__byteToString(self.__rightShift(packetChecksum, 0)))

        self.__logPackage("Write", packetType, len(packetPayload),
                          packetChecksum, packetPayload)

    def __wordToDecimal(self, wordBytes):
        return ustruct.unpack('>H', wordBytes)[0]

    def __clearPayloadBuffer(self):
        for i in range(len(self.__payloadBuffer)):
            self.__payloadBuffer[i] = 0

    def __readHeader(self):
        # TODO - timeout
        while (not self.__serial.any()):
            pass
        packageHeader = self.__serial.read(9)
        # Check the package header
        if (self.__wordToDecimal(packageHeader[0:2]) != FINGERPRINT_STARTCODE):
            print("Header error, payload:[%s]" %
                  ' '.join('0x{:02x}'.format(x) for x in packageHeader))
            raise Exception('Received package does not begin with a valid header!')
        packageType = packageHeader[6]
        return (packageType, packageHeader)

    def __readPackageHeader(self):
        packageType, packageHeader = self.__readHeader()
        # Calculate payload length, excluding checksum
        packagePayloadLength = self.__wordToDecimal(packageHeader[7:9]) - 2
        packageLengthSum = packageHeader[7] + packageHeader[8]
        return (packageType, packageLengthSum, packagePayloadLength)

    def __readAcknowledgementPackage(self):
        packageType, packageHeader = self.__readHeader()
        if (packageType != FINGERPRINT_ACKPACKET):
            raise Exception('The received packet is no ack packet!')
        confirmationCode = self.__serial.read(1)[0]
        receivedChecksum = self.__readChecksum()
        # TODO - verify checksum
        self.__logPackage("Read ", packageType,
                          1, receivedChecksum, [confirmationCode])
        return confirmationCode

    def __readChecksum(self):
        checksum = self.__serial.read(2)
        return self.__leftShift(checksum[0], 8) | checksum[1]

    def __logPackage(self, msg, type, payloadLength, checksum, payload):
        self._log.debug("%s type:0x%02x, length:%2d, checksum:%4d, payload:[%s]",
                        msg, type, payloadLength, checksum,
                        ' '.join('0x{:02x}'.format(x) for x in payload))

    def __readPacket(self):
        """
        Receive a packet from the sensor.

        Returns:
            A tuple that contain the following information:
            0: integer(1 byte) The packet type.
            1: integer(n bytes) The packet payload.

        Raises:
            Exception: if checksum is wrong
        """
        packageType, packageLengthSum, packagePayloadLength = self.__readPackageHeader()
        # Read package payload excluding checksum
        self.__clearPayloadBuffer()
        self.__serial.readinto(self.__payloadBuffer, packagePayloadLength)

        # Calculate checksum:
        # package type (1 byte) + header (2 bytes) + payload (n bytes)
        packetChecksum = (packageType + packageLengthSum
                          + sum(self.__payloadBuffer))

        # Verify checksum
        receivedChecksum = self.__readChecksum()
        if (receivedChecksum != packetChecksum):
            raise Exception('The received packet is corrupted (the checksum is wrong)!')

        self.__logPackage("Read ", packageType, packagePayloadLength,
                          packetChecksum,
                          memoryview(self.__payloadBuffer)[:packagePayloadLength])
        return (packageType, self.__payloadBuffer)

    def __handleAcknowledgement(self, confirmationCode, allowed=set()):
        if (confirmationCode == FINGERPRINT_OK or confirmationCode in allowed):
            pass
        elif (confirmationCode in FINGERPRINT_ERROR_CODES):
            raise Exception("%s (0x%02x)" % (FINGERPRINT_ERROR_CODES[confirmationCode], confirmationCode))
        else:
            raise Exception('Unknown error ' + hex(confirmationCode))

    def verifyPassword(self):
        """
        Verify password of the sensor.

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

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode,
                                     set([FINGERPRINT_ERROR_WRONGPASSWORD]))
        return (confirmationCode != FINGERPRINT_ERROR_WRONGPASSWORD)

    def setPassword(self, newPassword):
        """
        Set the password of the sensor.

        Arguments:
            newPassword (int): The new password to use.

        Raises:
            Exception: if an error occured
        """
        # Validate the password (maximum 4 bytes)
        if (newPassword < 0x00000000 or newPassword > 0xFFFFFFFF):
            raise ValueError('The given password is invalid!')

        packetPayload = (
            FINGERPRINT_SETPASSWORD,
            self.__rightShift(newPassword, 24),
            self.__rightShift(newPassword, 16),
            self.__rightShift(newPassword, 8),
            self.__rightShift(newPassword, 0),
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)
        self.__password = newPassword

    def setAddress(self, newAddress):
        """
        Set the sensor address.

        Arguments:
            newAddress (int): The new address to use.

        Raises:
            Exception: if any error occurs
        """
        # Validate the address (maximum 4 bytes)
        if (newAddress < 0x00000000 or newAddress > 0xFFFFFFFF):
            raise ValueError('The given address is invalid!')

        packetPayload = (
            FINGERPRINT_SETADDRESS,
            self.__rightShift(newAddress, 24),
            self.__rightShift(newAddress, 16),
            self.__rightShift(newAddress, 8),
            self.__rightShift(newAddress, 0),
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)
        self.__address = newAddress

    def setSystemParameter(self, parameterNumber, parameterValue):
        """
        Set a system parameter of the sensor.

        Arguments:
            parameterNumber (int): The parameter number. Use one of `FINGERPRINT_SETSYSTEMPARAMETER_*` constants.
            parameterValue (int): The value

        Raises:
            ValueError: if any passed parameter is invalid
            Exception: if any error occurs
        """
        # Validate the baud rate parameter
        if (parameterNumber == FINGERPRINT_SETSYSTEMPARAMETER_BAUDRATE):
            if (parameterValue < 1 or parameterValue > 12):
                raise ValueError('The given baud rate parameter is invalid!')
        # Validate the security level parameter
        elif (parameterNumber == FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL):
            if (parameterValue < 1 or parameterValue > 5):
                raise ValueError('The given security level parameter is invalid!')
        # Validate the package length parameter
        elif (parameterNumber == FINGERPRINT_SETSYSTEMPARAMETER_PACKAGE_SIZE):
            if (parameterValue < 0 or parameterValue > 3):
                raise ValueError('The given package length parameter is invalid!')
        # The parameter number is not valid
        else:
            raise ValueError('The given parameter number is invalid!')

        packetPayload = (
            FINGERPRINT_SETSYSTEMPARAMETER,
            parameterNumber,
            parameterValue,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

    def setBaudRate(self, baudRate):
        """
        Set the baud rate.

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
        Set the security level of the sensor.

        Arguments:
            securityLevel (int): Value between 1 and 5 where 1 is lowest and 5 highest.

        Raises:
            Exception: if any error occurs
        """
        self.setSystemParameter(FINGERPRINT_SETSYSTEMPARAMETER_SECURITY_LEVEL, securityLevel)

    def setMaxPacketSize(self, packetSize):
        """
        Set the maximum packet size of sensor.

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
        Get all available system information of the sensor.

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

        packetType, packetPayload = self.__readPacket()
        if (packetType != FINGERPRINT_ACKPACKET):
            raise Exception('The received packet is no ack packet!')

        # DEBUG: Read successfully
        if (packetPayload[0] == FINGERPRINT_OK):
            statusRegister     = self.__leftShift(packetPayload[1], 8) | self.__leftShift(packetPayload[2], 0)
            systemID           = self.__leftShift(packetPayload[3], 8) | self.__leftShift(packetPayload[4], 0)
            storageCapacity    = self.__leftShift(packetPayload[5], 8) | self.__leftShift(packetPayload[6], 0)
            securityLevel      = self.__leftShift(packetPayload[7], 8) | self.__leftShift(packetPayload[8], 0)
            deviceAddress      = ((packetPayload[9] << 8 | packetPayload[10]) << 8 | packetPayload[11]) << 8 | packetPayload[12]  # TODO
            packetLength       = self.__leftShift(packetPayload[13], 8) | self.__leftShift(packetPayload[14], 0)
            baudRate           = self.__leftShift(packetPayload[15], 8) | self.__leftShift(packetPayload[16], 0)

            return (statusRegister, systemID, storageCapacity, securityLevel, deviceAddress, packetLength, baudRate)
        else:
            self.__handleAcknowledgement(packetPayload[0])

    def getStorageCapacity(self):
        """
        Get the sensor storage capacity.

        Returns:
            The storage capacity (int).

        Raises:
            Exception: if any error occurs
        """
        return self.getSystemParameters()[2]

    def getSecurityLevel(self):
        """
        Get the security level of the sensor.

        Returns:
            The security level (int).

        Raises:
            Exception: if any error occurs
        """
        return self.getSystemParameters()[3]

    def getMaxPacketSize(self):
        """
        Get the maximum allowed size of a single packet.

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
        Get the baud rate.

        Returns:
            The baud rate (int).

        Raises:
            Exception: if any error occurs
        """
        return self.getSystemParameters()[6] * 9600

    def getTemplateIndex(self, page):
        """
        Get a list of the template positions with usage indicator.

        Arguments:
            page (int): The page (value between 0 and 3).

        Returns:
            The list.

        Raises:
            ValueError: if passed page is invalid
            Exception: if any error occurs
        """
        if (page < 0 or page > 3):
            raise ValueError('The given index page is invalid!')

        packetPayload = (
            FINGERPRINT_TEMPLATEINDEX,
            page,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        packageType, receivedPacket = self.__readPacket()
        self.__handleAcknowledgement(receivedPacket[0])

        # DEBUG: Read index table successfully
        templateIndex = []
        # Contain the table page bytes (skip the first status byte)
        pageElements = receivedPacket[1:]

        for pageElement in pageElements:
            # Test every bit (bit = template position is used indicator) of a table page element
            for p in range(0, 7 + 1):
                positionIsUsed = (self.__bitAtPosition(pageElement, p) == 1)
                templateIndex.append(positionIsUsed)

        return templateIndex

    def getTemplateCount(self):
        """
        Get the number of stored templates.

        Returns:
            The template count (int).

        Raises:
            Exception: if any error occurs
        """
        packetPayload = (
            FINGERPRINT_TEMPLATECOUNT,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        packageType, receivedPacket = self.__readPacket()
        self.__handleAcknowledgement(receivedPacket[0])

        return self.__wordToDecimal(receivedPacket[1:3])

    def readImage(self):
        """
        Read the image of a finger and store it in image buffer.

        Returns:
            True if image was read successfully or False otherwise.

        Raises:
            Exception: if any error occurs
        """
        packetPayload = (
            FINGERPRINT_READIMAGE,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode, set([FINGERPRINT_ERROR_NOFINGER]))

        return confirmationCode != FINGERPRINT_ERROR_NOFINGER

    def convertImage(self, charBufferNumber=FINGERPRINT_CHARBUFFER1):
        """
        Convert the image in image buffer to characteristics and store it in specified char buffer.

        Arguments:
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Raises:
            ValueError: if passed char buffer is invalid
            Exception: if any error occurs
        """
        self.__assertValidCharactisticBuffer(charBufferNumber)

        packetPayload = (
            FINGERPRINT_CONVERTIMAGE,
            charBufferNumber,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

    def createTemplate(self):
        """
        Combine the characteristics which are stored in char buffer 1 and char buffer 2 into one template.

        The created template will be stored again in char buffer 1 and char buffer 2 as the same.

        Returns:
            True if the two buffers match a single finger or False otherwise.

        Raises:
            Exception: if any error occurs
        """
        packetPayload = (
            FINGERPRINT_CREATETEMPLATE,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode, set([FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH]))
        return confirmationCode != FINGERPRINT_ERROR_CHARACTERISTICSMISMATCH

    def storeTemplate(self, positionNumber=-1, charBufferNumber=FINGERPRINT_CHARBUFFER1):
        """
        Store a template from the specified char buffer at the given position.

        Arguments:
            positionNumber (int): The position
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Returns:
            The position number (int) of the stored template.

        Raises:
            ValueError: if passed position or char buffer is invalid
            Exception: if any error occurs
        """
        # Find a free index
        if (positionNumber == -1):
            for page in range(0, 4):
                # Free index found?
                if (positionNumber >= 0):
                    break

                templateIndex = self.getTemplateIndex(page)

                for i in range(0, len(templateIndex)):
                    # Index not used?
                    if (templateIndex[i] is False):
                        positionNumber = (len(templateIndex) * page) + i
                        break

        if (positionNumber < 0x0000 or positionNumber >= self.getStorageCapacity()):
            raise ValueError('The given position number is invalid!')

        self.__assertValidCharactisticBuffer(charBufferNumber)

        packetPayload = (
            FINGERPRINT_STORETEMPLATE,
            charBufferNumber,
            self.__rightShift(positionNumber, 8),
            self.__rightShift(positionNumber, 0),
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)
        return positionNumber

    def searchTemplate(self, charBufferNumber=FINGERPRINT_CHARBUFFER1, positionStart=0, count=-1):
        """
        Search inside the database for the characteristics in char buffer.

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
        self.__assertValidCharactisticBuffer(charBufferNumber)

        if (count > 0):
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

        packageType, receivedPacket = self.__readPacket()
        self.__handleAcknowledgement(receivedPacket[0], set([FINGERPRINT_ERROR_NOTEMPLATEFOUND]))

        if (receivedPacket[0] == FINGERPRINT_ERROR_NOTEMPLATEFOUND):
            return (-1, -1)
        else:
            positionNumber = self.__wordToDecimal(receivedPacket[1:3])
            accuracyScore = self.__wordToDecimal(receivedPacket[3:5])
            return (positionNumber, accuracyScore)

    def loadTemplate(self, positionNumber, charBufferNumber=FINGERPRINT_CHARBUFFER1):
        """
        Load an existing template specified by position number to specified char buffer.

        Arguments:
            positionNumber (int): The position
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Raises:
            ValueError: if passed position or char buffer is invalid
            Exception: if any error occurs
        """
        if (positionNumber < 0x0000 or positionNumber >= self.getStorageCapacity()):
            raise ValueError('The given position number is invalid!')

        self.__assertValidCharactisticBuffer(charBufferNumber)

        packetPayload = (
            FINGERPRINT_LOADTEMPLATE,
            charBufferNumber,
            self.__rightShift(positionNumber, 8),
            self.__rightShift(positionNumber, 0),
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

    def deleteTemplate(self, positionNumber, count=1):
        """
        Delete templates from fingerprint database. Per default one.

        Arguments:
            positionNumber (int): The position
            count (int): The number of templates to be deleted.

        Raises:
            ValueError: if passed position or count is invalid
            Exception: if any error occurs
        """
        capacity = self.getStorageCapacity()

        if (positionNumber < 0x0000 or positionNumber >= capacity):
            raise ValueError('The given position number is invalid!')

        if (count < 0x0000 or count > capacity - positionNumber):
            raise ValueError('The given count is invalid!')

        packetPayload = (
            FINGERPRINT_DELETETEMPLATE,
            self.__rightShift(positionNumber, 8),
            self.__rightShift(positionNumber, 0),
            self.__rightShift(count, 8),
            self.__rightShift(count, 0),
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

    def clearDatabase(self):
        """
        Delete all templates from the fingeprint database.

        Raises:
            Exception: if any error occurs
        """
        packetPayload = (
            FINGERPRINT_CLEARDATABASE,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

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

        packetType, receivedPacket = self.__readPacket()
        self.__handleAcknowledgement(receivedPacket[0],
                                     set([FINGERPRINT_ERROR_NOTMATCHING]))

        if (receivedPacket[0] == FINGERPRINT_ERROR_NOTMATCHING):
            return 0
        else:
            return self.__wordToDecimal(receivedPacket[1:3])

    def __assertValidCharactisticBuffer(self, bufferNumber):
        if (bufferNumber != FINGERPRINT_CHARBUFFER1 and
                bufferNumber != FINGERPRINT_CHARBUFFER2):
            raise ValueError('The given char buffer number is invalid!')

    def uploadCharacteristics(self, charBufferNumber=FINGERPRINT_CHARBUFFER1, characteristicsData=[0]):
        """
        Upload finger characteristics to specified char buffer.

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
        self.__assertValidCharactisticBuffer(charBufferNumber)

        if (characteristicsData == [0]):
            raise ValueError('The characteristics data is required!')

        maxPacketSize = self.getMaxPacketSize()

        # Upload command
        packetPayload = (
            FINGERPRINT_UPLOADCHARACTERISTICS,
            charBufferNumber
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        # Get first reply packet
        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

        # Upload data packets
        packetNbr = len(characteristicsData) / maxPacketSize

        if (packetNbr <= 1):
            self.__writePacket(FINGERPRINT_ENDDATAPACKET, characteristicsData)
        else:
            i = 1
            while (i < packetNbr):
                lfrom = (i-1) * maxPacketSize
                lto = lfrom + maxPacketSize
                self.__writePacket(FINGERPRINT_DATAPACKET, characteristicsData[lfrom:lto])
                i += 1

            lfrom = (i-1) * maxPacketSize
            lto = lfrom + maxPacketSize
            self.__writePacket(FINGERPRINT_ENDDATAPACKET, characteristicsData[lfrom:lto])

        # Verify uploaded characteristics
        characterics = self.downloadCharacteristics(charBufferNumber)
        return (characterics == characteristicsData)

    def uploadCharacteristics2(self, characteristicsData,
                               charBufferNumber=FINGERPRINT_CHARBUFFER1):
        """
        Upload finger characteristics to specified char buffer.

        Arguments:
            characteristicsData (generator): The characteristics
            charBufferNumber (int): The char buffer. Use
            `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Raises:
            ValueError: if passed char buffer or characteristics are invalid
            Exception: if any error occurs
        """
        self.__assertValidCharactisticBuffer(charBufferNumber)

        # Upload command
        packetPayload = (
            FINGERPRINT_UPLOADCHARACTERISTICS,
            charBufferNumber
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        # Get acknowledgement package
        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

        count = 0
        self.__clearPayloadBuffer()
        for c in characteristicsData:
            if (count == 32):
                self.__writePacket(FINGERPRINT_DATAPACKET,
                                   memoryview(self.__payloadBuffer)[:count])
                self.__clearPayloadBuffer()
                count = 0

            self.__payloadBuffer[count] = c[0]
            count += 1

        self.__writePacket(FINGERPRINT_ENDDATAPACKET,
                           memoryview(self.__payloadBuffer)[:count])
        self.__clearPayloadBuffer()
        # TODO - reimplement success check

    def generateRandomNumber(self):
        """
        Generate a random 32-bit decimal number.

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

        packageType, receivedPacket = self.__readPacket()
        self.__handleAcknowledgement(receivedPacket[0])

        number = 0
        number = number | self.__leftShift(receivedPacket[1], 24)
        number = number | self.__leftShift(receivedPacket[2], 16)
        number = number | self.__leftShift(receivedPacket[3], 8)
        number = number | self.__leftShift(receivedPacket[4], 0)
        return number

    def downloadCharacteristics(self, charBufferNumber=FINGERPRINT_CHARBUFFER1):
        """
        Download the finger characteristics from the specified char buffer.

        Arguments:
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.
            characteristicsData (list): The characteristics

        Returns:
            The characteristics (list).

        Raises:
            ValueError: if passed char buffer is invalid
            Exception: if any error occurs
        """
        self.__assertValidCharactisticBuffer(charBufferNumber)

        packetPayload = (
            FINGERPRINT_DOWNLOADCHARACTERISTICS,
            charBufferNumber,
        )

        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        # Get first reply packet
        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

        completePayload = []

        # Get follow-up data packets until the last data packet is received
        receivedPacketType = None
        while (receivedPacketType != FINGERPRINT_ENDDATAPACKET):

            receivedPacket = self.__readPacket()

            receivedPacketType = receivedPacket[0]
            receivedPacketPayload = receivedPacket[1]

            if (receivedPacketType != FINGERPRINT_DATAPACKET and receivedPacketType != FINGERPRINT_ENDDATAPACKET):
                raise Exception('The received packet is no data packet!')

            for i in range(0, len(receivedPacketPayload)):
                completePayload.append(receivedPacketPayload[i])

        return completePayload

    def downloadCharacteristics2(self, charBufferNumber=FINGERPRINT_CHARBUFFER1):
        """
        Download the finger characteristics from the specified char buffer.

        Arguments:
            charBufferNumber (int): The char buffer. Use `FINGERPRINT_CHARBUFFER1` or `FINGERPRINT_CHARBUFFER2`.

        Returns:
            The characteristics (generator).

        Raises:
            ValueError: if passed char buffer is invalid
            Exception: if any error occurs
        """
        self.__assertValidCharactisticBuffer(charBufferNumber)

        packetPayload = (
            FINGERPRINT_DOWNLOADCHARACTERISTICS,
            charBufferNumber,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        # Get acknowledgement package
        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

        # Get follow-up data packets until the last data packet is received
        packageType = None
        while (packageType != FINGERPRINT_ENDDATAPACKET):
            packageType, packageLengthSum, packagePayloadLength = self.__readPackageHeader()
            if (packageType != FINGERPRINT_DATAPACKET and packageType != FINGERPRINT_ENDDATAPACKET):
                raise Exception('The received packet is no data packet!')

            # Read payload
            calculatedChecksum = (packageType + packageLengthSum)
            self.__clearPayloadBuffer()
            for i in range(0, packagePayloadLength):
                payloadByte = self.__serial.read(1)
                calculatedChecksum += payloadByte[0]
                self.__payloadBuffer[i] = payloadByte[0]
                yield payloadByte

            # Verify checksum
            checksum = self.__serial.read(2)
            receivedChecksum = self.__leftShift(checksum[0], 8) | checksum[1]

            self._log.debug("Download type:0x%02x, length:%3d, checksum:%4d(%4d), checksum:[%s], payload:[%s]",
                            packageType, packagePayloadLength,
                            receivedChecksum, calculatedChecksum,
                            ' '.join('0x{:02x}'.format(x) for x in checksum),
                            ' '.join('0x{:02x}'.format(x) for x in memoryview(self.__payloadBuffer)[:packagePayloadLength]))

            # if (receivedChecksum != packageChecksum):
            #     raise Exception('The received packet is corrupted (the checksum is wrong)!')
        self.__clearPayloadBuffer()

    def softReset(self):
        """Soft reset the sensor.

        Author:
            Chris Borrill <chris.borrill@gmail.com>

        Raises:
            Exception: if soft reset fails

        """
        packetPayload = (
            FINGERPRINT_SOFT_RESET,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

        # Wait for handshake on reset completion
        # TODO - timeout?
        while(self.__serial.read(1) != b'U'):
            pass

    def checkSensor(self):
        """Check the sensor is in a working state.

        Author:
            Chris Borrill <chris.borrill@gmail.com>

        Raises:
            Exception: if sensor not in a working state
        """
        packetPayload = (
            FINGERPRINT_CHECK_SENSOR,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

    def handshake(self):
        """Hand shake with the sensor.

        Author:
            Chris Borrill <chris.borrill@gmail.com>

        Raises:
            Exception: if sensor handshake fails
        """
        packetPayload = (
            FINGERPRINT_HANDSHAKE,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

    def clearBuffer(self):
        """Clear read buffer."""
        self.__serial.read()

    def cancelInstruction(self):
        """Cancel last intruction to the sensor.

        Author:
            Chris Borrill <chris.borrill@gmail.com>
        """
        packetPayload = (
            FINGERPRINT_CANCEL_INSTRUCTION,
        )
        self.__writePacket(FINGERPRINT_COMMANDPACKET, packetPayload)

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)

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

        confirmationCode = self.__readAcknowledgementPackage()
        self.__handleAcknowledgement(confirmationCode)
