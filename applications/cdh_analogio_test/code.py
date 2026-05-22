import analogio
import microcontroller
import board

if __name__ == "__main__":
    something = analogio.AnalogIn(microcontroller.pin.PA04)
    print(something.value)
    pass
