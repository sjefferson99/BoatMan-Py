import utime
import machine
from machine import Timer
import picodisplay

# Initialise Picodisplay with a bytearray display buffer
buf = bytearray(picodisplay.get_width() * picodisplay.get_height() * 2)
picodisplay.init(buf)
picodisplay.set_backlight(1.0)

picodisplay.set_pen(0, 255, 0)                    # Set a green pen
picodisplay.clear()                               # Clear the display buffer
picodisplay.set_pen(255, 255, 255)                # Set a white pen
picodisplay.text("BoatMan", 10, 10, 240, 4)  # Add some text
picodisplay.text("Boat Manager", 10, 50, 240, 2)  # Add some text
picodisplay.update()                              # Update the display with our changes

#Init LED outputs and controls
timer = Timer()
led = machine.Pin(25, machine.Pin.OUT)
ext_led1 = machine.PWM(machine.Pin(2))
ext_led1.freq(1000)
ext_led2 = machine.PWM(machine.Pin(3))
ext_led2.freq(1000)
ext_led3 = machine.PWM(machine.Pin(26))
ext_led3.freq(1000)
ext_led4 = machine.PWM(machine.Pin(5))
ext_led4.freq(1000)
ext_led5 = machine.PWM(machine.Pin(27))
ext_led5.freq(1000)
ext_led6 = machine.PWM(machine.Pin(0))
ext_led6.freq(1000)
ext_led7 = machine.PWM(machine.Pin(1))
ext_led7.freq(1000)
sw_a = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
sw_b = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
sw_x = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
sw_y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
fader = machine.ADC(28)

#init LED fader config
current_bank = 0
ledbanks = [65025, 65025, 65025, 65025, 65025, 65025, 0, 0]
bankbutton_press = 0

#General config
refresh = 1
current_mode = 0
modes = ["run", "lights", "misc"]

def toggleleddb(pin):
    timer.init(mode=Timer.ONE_SHOT, period=200, callback=toggleled)

def toggleled(pin):
    global ledbanks
    if ledbanks[current_bank] != 0:
        ledbanks[current_bank] = 0
        print(ledbanks[current_bank])
    else:
        ledbanks[current_bank] = fader.read_u16()
        print(ledbanks[current_bank])
    utime.sleep_ms(200)

def changebankdb(pin):
    timer.init(mode=Timer.ONE_SHOT, period=200, callback=changebank)

def changebank(pin):
    global bankbutton_press
    global current_bank
    global refresh

    refresh = 1
    
    bankbutton_press = utime.ticks_ms()
    
    while sw_b.value() == 0 and utime.ticks_diff(utime.ticks_ms(), bankbutton_press) < 1000:
        pass
    
    if utime.ticks_diff(utime.ticks_ms(), bankbutton_press) > 900:
        current_bank = 0
        print(current_bank)
    elif current_bank < 7:
        current_bank += 1
        print(current_bank)
    else:
        current_bank = 1
        print(current_bank)
    utime.sleep_ms(200)

def modeswitchdb(pin):
    timer.init(mode=Timer.ONE_SHOT, period=200, callback=modeswitch)

def modeswitch(pin):
    global current_mode
    global refresh
    
    refresh = 1
    if current_mode < 1:
        current_mode = 1
        print (current_mode)
    else:
        current_mode = 0
        print (current_mode)

sw_a.irq(toggleleddb, machine.Pin.IRQ_FALLING)
sw_b.irq(changebankdb, machine.Pin.IRQ_FALLING)
sw_x.irq(modeswitchdb, machine.Pin.IRQ_FALLING)

#init LEDs
if current_bank == 0:
    ext_led1.duty_u16(ledbanks[0])
    ext_led2.duty_u16(ledbanks[0])
    ext_led3.duty_u16(ledbanks[0])
    ext_led4.duty_u16(ledbanks[0])
    ext_led5.duty_u16(ledbanks[0])
    ext_led6.duty_u16(0)
    ext_led7.duty_u16(0)
else:
    ext_led1.duty_u16(ledbanks[1])
    ext_led2.duty_u16(ledbanks[2])
    ext_led3.duty_u16(ledbanks[3])
    ext_led4.duty_u16(ledbanks[4])
    ext_led5.duty_u16(ledbanks[5])
    ext_led6.duty_u16(ledbanks[6])
    ext_led7.duty_u16(ledbanks[7])

while True:
    if current_mode == 0 and refresh == 1:
        picodisplay.set_pen(0, 255, 0)
        picodisplay.clear()                
        picodisplay.set_pen(255, 255, 255)       
        picodisplay.text("BoatMan", 10, 10, 240, 4)
        picodisplay.text("Boat Manager", 10, 40, 240, 2)
        picodisplay.text("X: Mode", 10, 70, 240, 2)
        picodisplay.update()
        refresh = 0

    if current_mode == 1:
        if refresh == 1:
            picodisplay.set_pen(0, 255, 0)
            picodisplay.clear()                
            picodisplay.set_pen(255, 255, 255)       
            picodisplay.text("BoatMan", 10, 10, 240, 4)
            picodisplay.text("Boat Manager", 10, 40, 240, 2)
            picodisplay.text("Light Config - Bank: " + str(current_bank), 10, 70, 240, 2)
            picodisplay.text("X: Mode", 10, 100, 240, 2)
            picodisplay.update()
            refresh = 0

        if ledbanks[current_bank] > 0:
                ledbanks[current_bank] = fader.read_u16()
        
        if current_bank == 0:
            ext_led1.duty_u16(ledbanks[0])
            ext_led2.duty_u16(ledbanks[0])
            ext_led3.duty_u16(ledbanks[0])
            ext_led4.duty_u16(ledbanks[0])
            ext_led5.duty_u16(ledbanks[0])
            ext_led6.duty_u16(0)
            ext_led7.duty_u16(0)
        else:
            ext_led1.duty_u16(ledbanks[1])
            ext_led2.duty_u16(ledbanks[2])
            ext_led3.duty_u16(ledbanks[3])
            ext_led4.duty_u16(ledbanks[4])
            ext_led5.duty_u16(ledbanks[5])
            ext_led6.duty_u16(ledbanks[6])
            ext_led7.duty_u16(ledbanks[7])