"""
Raw-payload UART test for the Orion G16 driver.

This script uses the current `oriong16.py` driver, sends the binary-output
command, and prints the most recent raw payload frame in hex whenever it
changes. Update the UART pin names below to match the wiring under test.
"""

import time

import microcontroller as mc

import oriong16


UART_TX_PIN_NAMES = ("PD01",)
UART_RX_PIN_NAMES = ("PD00",)
POLL_INTERVAL_S = 0.1
STATUS_INTERVAL_S = 1.0


def _get_pin(*pin_names):
    for pin_name in pin_names:
        pin = getattr(mc.pin, pin_name, None)
        if pin is not None:
            return pin
    raise AttributeError("No matching microcontroller pin found for {}".format(pin_names))


def _hex_bytes(data):
    if not data:
        return "<none>"
    return " ".join("{:02X}".format(byte) for byte in data)


def main():
    tx_pin = _get_pin(*UART_TX_PIN_NAMES)
    rx_pin = _get_pin(*UART_RX_PIN_NAMES)

    print(
        "Starting Orion raw-payload test on TX={} RX={} baud={}".format(
            UART_TX_PIN_NAMES[0],
            UART_RX_PIN_NAMES[0],
            oriong16.BAUDRATE,
        )
    )

    gps = oriong16.GPS(tx_pin, rx_pin)
    gps.connect()
    print("Sent Orion binary-output command.")

    last_payload = b""
    last_status_time = time.monotonic()
    total_rx_bytes = 0

    while True:
        pending_before = gps.uart.in_waiting
        total_rx_bytes += pending_before
        gps.update()

        payload = bytes(gps.raw_payload)
        now = time.monotonic()
        if payload and payload != last_payload:
            print(
                "raw_payload len={} msg_id=0x{:02X} data={}".format(
                    len(payload),
                    payload[0],
                    _hex_bytes(payload),
                )
            )
            last_payload = payload
            last_status_time = now
        elif (now - last_status_time) >= STATUS_INTERVAL_S:
            print(
                "status: pending_before={}, total_rx_bytes~={}, raw_len={}, "
                "fix_mode={}, satellites={}".format(
                    pending_before,
                    total_rx_bytes,
                    len(payload),
                    gps.fix_mode,
                    gps.satellites,
                )
            )
            last_status_time = now

        time.sleep(POLL_INTERVAL_S)


if __name__ == "__main__":
    main()
