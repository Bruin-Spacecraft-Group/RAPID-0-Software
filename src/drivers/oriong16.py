"""
Driver module for Orion G16 GPS module.
"""

import busio

BAUDRATE = 115200


class GPS:
    """
    GPS Class with methods to initialize and update the information being read.
    """

    def __init__(self, txd, rxd):
        self.uart = busio.UART(txd, rxd, baudrate=BAUDRATE, receiver_buffer_size=256)
        self.buffer = bytearray()

        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0  # Altitude above sea level (meters)

        self.fix_mode = 0
        self.satellites = 0
        self.raw_payload = bytearray()

    def connect(self):
        """
        Send a string to the GPS to convert it into binary output instead of NMEA.
        """
        self.uart.write(b"\xa0\xa1\x00\x03\x09\x02\x00\x0b\x0d\x0a")

    def update(self):
        """
        Update the buffer storing the incoming message from the GPS module, and determine when to parse to get information.
        """
        if self.uart.in_waiting > 0:
            self.buffer.extend(self.uart.read(self.uart.in_waiting))

        while len(self.buffer) >= 7:

            if self.buffer[0] != 0xA0 or self.buffer[1] != 0xA1:
                self.buffer.pop(0)
                continue

            payload_length = (self.buffer[2] << 8) | self.buffer[3]

            total_msg_len = 4 + payload_length + 3

            if len(self.buffer) < total_msg_len:
                break

            payload = self.buffer[4 : 4 + payload_length]
            self.raw_payload = payload
            checksum_byte = self.buffer[4 + payload_length]

            calculated_cs = 0
            for byte in payload:
                calculated_cs ^= byte

            if calculated_cs == checksum_byte:
                self.parse_payload(payload)

            self.buffer = self.buffer[total_msg_len:]

    def bytes_to_int32(self, b0, b1, b2, b3):
        """
        Helper function to turn the bytes into a 32 bit signed integer.
        """
        val = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3

        if val >= 0x80000000:
            val -= 0x100000000

        return val

    def parse_payload(self, payload):
        """
        Parse the actual payload and extract data for latitude, longitude, etc. (Results in 32 bit integers).
        """
        msg_id = payload[0]

        if msg_id == 0xA8 and len(payload) >= 25:
            self.fix_mode = payload[1]
            self.satellites = payload[2]

            self.altitude = self.bytes_to_int32(
                payload[21], payload[22], payload[23], payload[24]
            )

            lat_raw = self.bytes_to_int32(
                payload[9], payload[10], payload[11], payload[12]
            )

            lon_raw = self.bytes_to_int32(
                payload[13], payload[14], payload[15], payload[16]
            )

            # Conver latitude and longitude to floating point values
            self.latitude = lat_raw / 10000000.0
            self.longitude = lon_raw / 10000000.0
