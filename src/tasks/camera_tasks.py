from drivers.camera import *
import usb_cdc


def capture_single_image(return_bursts):
    """
    Captures a single image and returns the bytes which can be compiled into a JPEG.

    Sends data in bursts of bytearray objects if return_bursts is true, or in one bytearray if false.
    """
    once_number = 128
    buffer = bytearray(once_number)

    camera = Camera()
    camera.Camera_Detection()
    camera.Spi_Test()
    camera.Camera_Init()
    camera.Spi_write(ARDUCHIP_TIM,VSYNC_LEVEL_MASK)
    utime.sleep(1)
    camera.clear_fifo_flag()
    camera.Spi_write(ARDUCHIP_FRAMES,0x00)
    camera.wrSensorRegs16_8(ov5642_640x480)

    camera.flush_fifo()  # Clear FIFO
    camera.clear_fifo_flag()
    camera.start_capture()  # Start the capture

    # Wait until capture is done
    while not camera.get_bit(0x41, 0x08):  # CAP_DONE_MASK
        utime.sleep(15)

    # Read the image data length
    image_length = camera.read_fifo_length()
    if image_length == 0 or image_length > 0x7FFFFF:  # Check FIFO size limit
        print("Error: Invalid image length")
        return None

    # Retrieve image data
    camera.SPI_CS_LOW()
    camera.set_fifo_burst()

    if return_bursts:
        image_data = bytearray(image_length)
        camera.spi.readinto(image_data)
    else:
        # TODO: Test this and decide how we want to send data back to ground
        count = 0
        while True:
            camera.spi.readinto(buffer, start = 0, end = once_number)
            #usb_cdc.data.write(buffer)
            utime.sleep(0.00015)
            print(buffer)
            count += once_number
            if count + once_number > image_length:
                count = image_length - count
                camera.spi.readinto(buffer, start = 0, end = count)
                #usb_cdc.data.write(buffer)
                print(buffer)
                camera.SPI_CS_HIGH()
                camera.clear_fifo_flag()
                break

    camera.SPI_CS_HIGH()

    # Clear the FIFO after reading
    camera.clear_fifo_flag()

    # Send image data via USB
    usb_cdc.data.write(image_data)
    return image_data
