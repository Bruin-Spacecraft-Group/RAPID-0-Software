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

    # pins defined for the STM32H743
    pm = pin_manager.PinManager.get_instance() 
    led_gpio = pm.create_digital_in_out(board.LED1)
    with led_gpio as led:
        led.direction = digitalio.Direction.OUTPUT

    uart_bus = pm.create_uart(microcontroller.pin.PB13, microcontroller.pin.PB12, baudrate=50000)

    te_rs485 = pm.create_digital_in_out(microcontroller.pin.PA15)
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



async def inter_subsystem_rs485_reciever_task():
    """
    Task that receives any RS485 message and lights up the LED for 1 second if successfully received data.
    """
    # pins defined for the STM32H743
    pm = pin_manager.PinManager.get_instance() 
    led_gpio = pm.create_digital_in_out(board.LED1)
    with led_gpio as led:
        led.direction = digitalio.Direction.OUTPUT

    uart_bus = pm.create_uart(microcontroller.pin.PB13, microcontroller.pin.PB12, baudrate=50000)

    te_rs485 = pm.create_digital_in_out(microcontroller.pin.PA15)
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