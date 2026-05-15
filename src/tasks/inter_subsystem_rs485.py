"""
Module for intersubsystem communication using UART over RS485
"""

import asyncio
import digitalio
import pin_manager

async def nucleo_rs485_sender_task(rs485_TX, rs485_RX, rs485_DE, rs485_LED):
    """
    Task that sends 0xFFEEDDCC and lights up the LED for 1 second if write is successful.
    """

    # pins defined for the STM32H743 Nucleo
    pm = pin_manager.PinManager.get_instance()
    led_gpio = pm.create_digital_in_out(rs485_LED)
    with led_gpio as led:
        led.direction = digitalio.Direction.OUTPUT

    uart_bus = pm.create_uart(rs485_TX, rs485_RX, baudrate=50000)

    te_rs485 = pm.create_digital_in_out(rs485_DE)
    with te_rs485 as te:
        te.direction = digitalio.Direction.OUTPUT


    while True:
        with te_rs485 as te:
            te.value = True

        data = bytearray([0] * 4)
        data[0] = 0xFF
        data[1] = 0xEE
        data[2] = 0xDD
        data[3] = 0xCC

        print("Data to be sent: ", list(data))

        with uart_bus as uart:
            write = uart.write(data)

        with te_rs485 as te:
            te.value = False

        if write:
            with led_gpio as led:
                led.value = True
            print("Data sent, number of bytes sent: ", write)
            await asyncio.sleep(1)
            with led_gpio as led:
                led.value = False
            await asyncio.sleep(1)
        else:
            print("Error sending data")


async def nucleo_rs485_receiver_task(rs485_TX, rs485_RX, rs485_DE, rs485_LED):
    """
    Task that receives any RS485 message and lights up the LED for 1 second if successfully received data.
    """
    # pins defined for the STM32H743 Nucleo
    pm = pin_manager.PinManager.get_instance()
    led_gpio = pm.create_digital_in_out(rs485_LED)
    with led_gpio as led:
        led.direction = digitalio.Direction.OUTPUT

    uart_bus = pm.create_uart(rs485_TX, rs485_RX, baudrate=50000)

    te_rs485 = pm.create_digital_in_out(rs485_DE)
    with te_rs485 as te:
        te.direction = digitalio.Direction.OUTPUT
        te.value = False


    while True:
        with uart_bus as uart:
            data = uart.read(32)  # read up to 32 bytes

        if data is not None:
            with led_gpio as led:
                led.value = True
            print("Data received: ", list(data))
            await asyncio.sleep(1)
            with led_gpio as led:
                led.value = False
            await asyncio.sleep(1)

        else:
            print("Error receiving data")


async def cdh_em_board_rs485_send_task(rs485_TX, rs485_RX, DE):
    """
    Task that sends 0xFFEEDDCC.
    """

    # pins defined for the CDH_EM_Board
    pm = pin_manager.PinManager.get_instance()

    uart_bus = pm.create_uart(rs485_TX, rs485_RX, baudrate=50000)

    te_rs485 = pm.create_digital_in_out(rs485_DE)
    with te_rs485 as te:
        te.direction = digitalio.Direction.OUTPUT


    while True:
        with te_rs485 as te:
            te.value = True

        data = bytearray([0] * 4)
        data[0] = 0xFF
        data[1] = 0xEE
        data[2] = 0xDD
        data[3] = 0xCC

        print("Data to be sent: ", list(data))

        with uart_bus as uart:
            write = uart.write(data)

        with te_rs485 as te:
            te.value = False

        if write:
            print("Data sent, number of bytes sent: ", write)
            await asyncio.sleep(1)
            await asyncio.sleep(1)
        else:
            print("Error sending data")


async def cdh_em_board_rs485_receiver_task(rs485_TX, rs485_RX, DE):
    """
    Task that receives any RS485 message and prints the received data.
    """
    # pins defined for the STM32H743 Nucleo
    pm = pin_manager.PinManager.get_instance()

    uart_bus = pm.create_uart(rs485_TX, rs485_RX, baudrate=50000)

    te_rs485 = pm.create_digital_in_out(rs485_DE)
    with te_rs485 as te:
        te.direction = digitalio.Direction.OUTPUT
        te.value = False


    while True:
        with uart_bus as uart:
            data = uart.read(32)  # read up to 32 bytes

        if data is not None:
            print("Data received: ", list(data))
            # await asyncio.sleep(1)

        else:
            print("Error receiving data")
