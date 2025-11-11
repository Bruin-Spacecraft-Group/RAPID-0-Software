import pwmio
import microcontroller
import time

pwm = pwmio.PWMOut(microcontroller.pin.PA00)

print("Running the code")

while True:
    pwm.duty_cycle = 0
