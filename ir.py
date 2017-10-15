import machine
import gc

@micropython.viper
def loop(n:int):
    for i in range(n):
        pass

@micropython.viper
def do_toggle(n:int):
    GPIO_OUT = ptr32(0x60000300) # GPIO base register
    for i in range(n):
        GPIO_OUT[1] = 0x10 # set bit 4
        for j in range(51):
            pass
        GPIO_OUT[2] = 0x10 # clear bit 4
        for j in range(51):
            pass

@micropython.viper
def output_ir_command(data, n:int):
    cnt = ptr16(data)
    for i in range(0, n, 2):
        do_toggle(cnt[i])
        loop(cnt[i+1]*10)


data = bytearray(2000)
pin = machine.Pin(4, machine.Pin.OUT, value=0)
Commands = [
    # here is a list of IR command files
    "cmd0.bin",
    "cmd1.bin",
    "cmd1.bin",
]


def send_ir_command(index):
    with open(Commands[index], "rb") as f:
        length = f.readinto(data)

    gc.disable()
    isr = machine.disable_irq()

    try:
        output_ir_command(data, length // 2)
    finally:
        machine.enable_irq(isr)
        gc.enable()