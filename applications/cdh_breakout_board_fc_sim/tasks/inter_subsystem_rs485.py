"""
Task to communicate with other subsystems over an RS485 bus.
"""

import asyncio
import board
import microcontroller
import busio
import digitalio
import pin_manager

async def inter_subsystem_rs485_sender_task():
    """
    Task that sends 0xFFEEDDCC and lights up the LED for 1 second if write is successful.
    """
    
    #led = digitalio.DigitalInOut(board.LED1) # OLD
    led = pin_manager.PinManager.get_instance()
    led.create_digital_in_out(board.LED1) # should be all that's needed for context managing
    
    led.direction = digitalio.Direction.OUTPUT

    uart = busio.UART(
        microcontroller.pin.PB13, microcontroller.pin.PB12, baudrate=50000
    )
    # pins defined for the STM32H743

    te = digitalio.DigitalInOut(microcontroller.pin.PA15)
    te.direction = digitalio.Direction.OUTPUT

    while True:
        DATA1 = 0xFF000000
        DATA2 = 0xEE0000
        DATA3 = 0xDD00
        DATA4 = 0xCC
        
        te.value = True
        data = bytearray([0] * 4)
        data[0] = (DATA1) >> 24
        data[1] = (DATA2) >> 16
        data[2] = (DATA3) >> 8
        data[3] = (DATA4) >> 0

        print("Data to be sent: ", list(data))

        write = uart.write(data)
        te.value = False

        if write:
            led.value = True
            print("Data sent, number of bytes sent: ", write)
            await asyncio.sleep(1)
            led.value = False
            await asyncio.sleep(1)
        else:
            print("Error sending data")
