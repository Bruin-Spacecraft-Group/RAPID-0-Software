import board
import microcontroller
import digitalio
import busio
import spitarget

import asyncio
import time
from Arducam import *

mode = 0
start_capture = 0
stop_flag=0
once_number=128
value_command=0
flag_command=0
buffer=bytearray(once_number)

mycam = ArducamClass(OV5642)
mycam.Camera_Detection()
mycam.Spi_Test()
mycam.Camera_Init()
mycam.Spi_write(ARDUCHIP_TIM,VSYNC_LEVEL_MASK)
utime.sleep(1)
mycam.clear_fifo_flag()
mycam.Spi_write(ARDUCHIP_FRAMES,0x00)
mycam.wrSensorRegs16_8(ov5642_640x480)


def read_fifo_burst():
    count=0
    lenght=mycam.read_fifo_length()
    mycam.SPI_CS_LOW()
    mycam.set_fifo_burst()
    while True:
        mycam.spi.readinto(buffer,start=0,end=once_number)
        #usb_cdc.data.write(buffer)
        utime.sleep(0.00015)
        print(buffer)
        count+=once_number
        if count+once_number>lenght:
            count=lenght-count
            mycam.spi.readinto(buffer,start=0,end=count)
            #usb_cdc.data.write(buffer)
            print(buffer)
            mycam.SPI_CS_HIGH()
            mycam.clear_fifo_flag()
            break


"""
inter_subsystem_spi_bus = spitarget.SPITarget(
    sck=microcontroller.pin.PA17,
    mosi=microcontroller.pin.PA16,
    miso=microcontroller.pin.PA19,
    ss=microcontroller.pin.PA18
)

async def send_receive(transmit_buffer, receive_buffer):
    inter_subsystem_spi_bus.load_packet(
        mosi_packet=receive_buffer,
        miso_packet=transmit_buffer
    )
    while not inter_subsystem_spi_bus.try_transfer():
        await asyncio.sleep(0)

sensorValue = 0x10203040
spiReadBytes = bytearray([0] * 4)
spiWriteBytes = bytearray([0] * 4)

async def spiWriteTask():
    global spiReadBytes, spiWriteBytes, sensorValue, inter_subsystem_spi_bus
    while True:
        # communicates commands with subsystem X
        spiWriteBytes[0] = (sensorValue & 0xFF000000) >> 24
        spiWriteBytes[1] = (sensorValue & 0xFF0000) >> 16
        spiWriteBytes[2] = (sensorValue & 0xFF00) >> 8
        spiWriteBytes[3] = (sensorValue & 0xFF) >> 0
        await send_receive(spiWriteBytes, spiReadBytes)

async def sensorReadTask():
    # regularly updates `sensorValue` based on the feedback from the sensor
    global sensorValue
    while True:
        sensorValue += 1
        await asyncio.sleep(0.2)

async def feedbackTask():
    # send debug data to the USB serial regularly
    global sensorValue, spiReadBytes, spiWriteBytes
    while True:
        print("TST wrote", list(bytes(spiWriteBytes)), "to SPI")  # fix with [:-1]
        print("TST read", list(bytes(spiReadBytes)), "from SPI")  # fix with [:-1]
        await asyncio.sleep(1)

async def gatheredTask():
    await asyncio.gather(feedbackTask(), spiWriteTask(), sensorReadTask())

asyncio.run(gatheredTask())
"""

print("Code.py bypassed (for camera)")


mycam.flush_fifo()
mycam.clear_fifo_flag()
mycam.start_capture()
read_fifo_burst()

import usb_cdc

def capture_single_image():
    mycam.flush_fifo()  # Clear FIFO
    mycam.clear_fifo_flag()
    mycam.start_capture()  # Start the capture

    # Wait until capture is done
    while not mycam.get_bit(0x41, 0x08):  # CAP_DONE_MASK
        utime.sleep(15)

    # Read the image data
    image_length = mycam.read_fifo_length()
    if image_length == 0 or image_length > 0x7FFFFF:  # Check FIFO size limit
        print("Error: Invalid image length")
        return None

    # Retrieve image data
    mycam.SPI_CS_LOW()
    mycam.set_fifo_burst()
    print("image data")
    print(image_length)
    image_data = bytearray(image_length)
    print("array initialized")
    mycam.spi.readinto(image_data)
    mycam.SPI_CS_HIGH()

    # Clear the FIFO after reading
    mycam.clear_fifo_flag()

    # Send image data via USB
    usb_cdc.data.write(image_data)
    return image_data
