import digitalio

import asyncio


class ADS1118_MUX_SELECT:
    CH0_SINGLE_END = 4
    CH1_SINGLE_END = 5
    CH2_SINGLE_END = 6
    CH3_SINGLE_END = 7
    CH0_CH1_DIFF = 0
    CH0_CH3_DIFF = 1
    CH1_CH3_DIFF = 2
    CH2_CH3_DIFF = 3
    TEMPERATURE = 255


class ADS1118_FSR:
    FSR_6144V = 0
    FSR_4096V = 1
    FSR_2048V = 2
    FSR_1024V = 3
    FSR_0512V = 4
    FSR_0256V = 5  # 6 and 7 are also valid here


class ADS1118_SAMPLE_RATE:
    RATE_8 = 0
    RATE_16 = 1
    RATE_32 = 2
    RATE_64 = 3
    RATE_128 = 4
    RATE_250 = 5
    RATE_475 = 6
    RATE_860 = 7


# When running on an spi bus slower than 40 kHz, async transfers should be used
# to maintain responsiveness of all tasks. When running on an spi bus which is
# faster than this, the overhead of ayncio context switching dominates the time
# taken, and synchronous transfers are more efficient.
ADS1118_ASYNC_TRANSFER = False


class ADS1118:
    def __init__(self, spi_device):
        self.spi_device = spi_device
        self.data_ready = digitalio.DigitalInOut(spi_device.get_MISO_pin())

    # Returns either the voltage in volts, or the temperature in degrees Celsius
    async def take_sample(
        self,
        channel,
        input_range=ADS1118_FSR.FSR_4096V,
        sample_rate=ADS1118_SAMPLE_RATE.RATE_128,
    ):
        ADS1118._check_sampling_params(channel, input_range, sample_rate)
        transmit_buffer = ADS1118._build_config_register_bytearray(
            channel, input_range, sample_rate
        )
        receive_buffer = bytearray([0, 0])

        if ADS1118_ASYNC_TRANSFER:
            await self.spi_device.async_transfer(transmit_buffer, receive_buffer)
        else:
            while not self.spi_device.get_spi().try_lock():
                await asyncio.sleep(0)
            self.spi_device.get_chip_select_pin().value = False
            self.spi_device.get_spi().write_readinto(transmit_buffer, receive_buffer)
            self.spi_device.get_chip_select_pin().value = True
            self.spi_device.get_spi().unlock()

        data_ready = False
        while not data_ready:
            await asyncio.sleep(0)
            while not self.spi_device.get_spi().try_lock():
                await asyncio.sleep(0)

            self.spi_device.get_chip_select_pin().value = False
            await asyncio.sleep(100e-9)  # CS to DRDY propogation time
            data_ready = not self.data_ready.value
            self.spi_device.get_chip_select_pin().value = True
            self.spi_device.get_spi().unlock()

        if ADS1118_ASYNC_TRANSFER:
            await self.spi_device.async_transfer(transmit_buffer, receive_buffer)
        else:
            while not self.spi_device.get_spi().try_lock():
                await asyncio.sleep(0)
            self.spi_device.get_chip_select_pin().value = False
            self.spi_device.get_spi().write_readinto(transmit_buffer, receive_buffer)
            self.spi_device.get_chip_select_pin().value = True
            self.spi_device.get_spi().unlock()

        if channel == ADS1118_MUX_SELECT.TEMPERATURE:
            return ADS1118._temperature_from_bytes(receive_buffer)
        else:
            return ADS1118._voltage_from_bytes(receive_buffer, input_range)

    def _check_sampling_params(channel, input_range, sample_rate):
        assert channel == ADS1118_MUX_SELECT.TEMPERATURE or (
            type(channel) == int and channel >= 0 and channel < 8
        )
        assert type(input_range) == int and input_range >= 0 and input_range < 8
        assert type(sample_rate) == int and sample_rate >= 0 and sample_rate < 8

    def _build_config_register_bytearray(channel, input_range, sample_rate):
        return bytearray(
            [
                (0b1 << 7)
                | ((channel & 0b111) << 4)
                | ((input_range & 0b111) << 1)
                | 1,
                ((sample_rate & 0b111) << 5)
                | ((channel == ADS1118_MUX_SELECT.TEMPERATURE) << 4)
                | 0b1010,
            ]
        )

    def _temperature_from_bytes(receive_buffer):
        reading = int.from_bytes(receive_buffer, "big", signed=True) >> 2
        return reading * 0.03125

    def _voltage_from_bytes(receive_buffer, fsr):
        lsb_size = dict(
            [
                (ADS1118_FSR.FSR_6144V, 187.5e-6),
                (ADS1118_FSR.FSR_4096V, 125e-6),
                (ADS1118_FSR.FSR_2048V, 62.5e-6),
                (ADS1118_FSR.FSR_1024V, 31.25e-6),
                (ADS1118_FSR.FSR_0512V, 15.625e-6),
                (ADS1118_FSR.FSR_0256V, 7.8125e-6),
            ]
        )[fsr]
        return int.from_bytes(receive_buffer, "big", signed=True) * lsb_size
