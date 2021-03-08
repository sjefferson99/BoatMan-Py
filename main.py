import utime
import machine
from machine import Timer
import picodisplay

# Initialise Picodisplay with a bytearray display buffer
print("initialising display")
buf = bytearray(picodisplay.get_width() * picodisplay.get_height() * 2)
picodisplay.init(buf)
picodisplay.set_backlight(1.0)

picodisplay.set_pen(0, 255, 0)                      # Set a green pen
picodisplay.clear()                                 # Clear the display buffer
picodisplay.set_pen(255, 255, 255)                  # Set a white pen
picodisplay.text("BoatMan", 10, 10, 240, 4)         # Add some text
picodisplay.text("Boat Manager", 10, 50, 240, 2)    # Add some text
picodisplay.update()                                # Update the display with our changes

#Init LED outputs and controls
print("initialising IO")
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
BUTTON_A = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)
BUTTON_B = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)
BUTTON_X = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
BUTTON_Y = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
fader = machine.ADC(28)

#init LED fader config
print("initialising LED values")
current_bank = 0    #Default to global bank
ledbanks = [65025, 65025, 65025, 65025, 65025, 65025, 0, 0] #default duty values: 0 - Global - all white LEDs, 1-7 - individual LED strips

#buttons and debounce
print("initialising buttons")
int_sample_freq = 10                            #Button debounce integrator sample frequenccy
debounce_time = 0.1                             #seconds to debounce for
int_max = int(int_sample_freq * debounce_time)  #integrator max value for button is pressed

button_integrators = {"BUTTON_A" : 0, "BUTTON_B" : 0, "BUTTON_X" : 0, "BUTTON_Y" : 0}   #button debounce integrator values
button_int_state = {"BUTTON_A" : 0, "BUTTON_B" : 0, "BUTTON_X" : 0, "BUTTON_Y" : 0}     #button integrator output last state
button_times = {"BUTTON_A" : 0, "BUTTON_B" : 0, "BUTTON_X" : 0, "BUTTON_Y" : 0}         #button press time
button_short = {"BUTTON_A" : 0, "BUTTON_B" : 0, "BUTTON_X" : 0, "BUTTON_Y" : 0}         #dictionary lookup of short pressed detection on buttons
button_long = {"BUTTON_A" : 0, "BUTTON_B" : 0, "BUTTON_X" : 0, "BUTTON_Y" : 0}          #dictionary lookup of long pressed detection on buttons

longpresstime = 1000    #button long press time in milliseconds

#General config
print("initialising general config")
refresh = 1     #screen refresh needed
current_mode = 0
modes = ["run", "lights", "misc"]

#Button functions
print("initialising functions")
#timer handler uses an integrator to debounce button presses and assign short or long press values based on time comparisons
def button_debounce(timer):
    global button_integrators
    global button_long
    global button_short
    global button_times

    for button in button_integrators:

        if picodisplay.is_pressed(getattr(picodisplay, button)):    #Integrate button pressed this sample
            if button_integrators[button] < int_max:
                button_integrators[button] += 1
        
        if picodisplay.is_pressed(getattr(picodisplay, button)) == False: #Integrate button not pressed this sample
            if button_integrators[button] > 0:
                button_integrators[button] -= 1
    
        if button_integrators[button] == 0:         #integrator hit button value of 0
            #print("Button low: " + button)
            if button_int_state[button] == 1:       #on transition to 0 from 1
                button_short[button] = 1
                print("Short " + button)
                if utime.ticks_diff(utime.ticks_ms(), button_times[button]) > longpresstime:    #set long press if it's been long enough
                    button_long[button] = 1
                    print("Long " + button)
            button_int_state[button] = 0
            
        if button_integrators[button] >= int_max:   #integrator hit button value of 1
            button_integrators[button] = int_max    #reset integrator in case corrupted
            print("Button High " + button)
            if button_int_state[button] == 0:
                button_times[button] = utime.ticks_ms()     #set transition high time if previous state was low
                print("Setting button high time")
            button_int_state[button] = 1    

#int_sample_freq seconds timer for button states
print("initialising timer")
tim = Timer()
tim.init(freq=int_sample_freq, mode=Timer.PERIODIC, callback=button_debounce)

#toggle LED to off or fader value
print("entering toggle LED function")
def toggleled(ledbanks):
    if ledbanks[current_bank] != 0:
        ledbanks[current_bank] = 0
        print(ledbanks[current_bank])
    else:
        ledbanks[current_bank] = fader.read_u16()
        print(ledbanks[current_bank])
    return ledbanks

def changebank(current_bank): #increment through LED banks
    if current_bank < 7:
        current_bank += 1
        print(current_bank)
    else:
        current_bank = 1
        print(current_bank)
    return current_bank

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

#init LEDs
print("initialising LEDs")
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

print("entering program loop")

while True:
    if current_mode == 0:   #run mode
        if refresh == 1:    #Update display
            print("refreshing display")
            picodisplay.set_pen(0, 255, 0)
            picodisplay.clear()                
            picodisplay.set_pen(255, 255, 255)       
            picodisplay.text("BoatMan", 10, 10, 240, 4)
            picodisplay.text("Boat Manager", 10, 40, 240, 2)
            picodisplay.text("X: Mode", 10, 70, 240, 2)
            picodisplay.update()
            refresh = 0

        if button_short["BUTTON_X"]:    #change mode
            current_mode = 1
            refresh = 1
            button_short["BUTTON_X"] = 0

    if current_mode == 1:   #In light config mode
        if button_short["BUTTON_A"]:    #toggle current led bank 0 or fader value
            ledbanks = toggleled(ledbanks)
            refresh = 1
            button_short["BUTTON_A"] = 0

        if button_short["BUTTON_B"]:    #increment current LED bank in cycle
            current_bank = changebank(current_bank)
            refresh = 1
            button_short["BUTTON_B"] = 0

        if button_long["BUTTON_B"]:    #Switch to global LED bank
            current_bank = 0
            refresh = 1
            button_long["BUTTON_B"] = 0

        if refresh == 1:    #Update display
            print("refreshing display")
            picodisplay.set_pen(0, 255, 0)
            picodisplay.clear()                
            picodisplay.set_pen(255, 255, 255)       
            picodisplay.text("BoatMan", 10, 10, 240, 4)
            picodisplay.text("Boat Manager", 10, 40, 240, 2)
            picodisplay.text("Light Config - Bank: " + str(current_bank), 10, 70, 240, 2)
            picodisplay.text("X: Mode", 10, 100, 240, 2)
            picodisplay.update()
            refresh = 0

        #Apply fader value only if bank is on
        if ledbanks[current_bank] > 0:
                ledbanks[current_bank] = fader.read_u16()
        
        #Update LED duty cycles for global or individual modes
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
        
        if button_short["BUTTON_X"]:    #change mode
            current_mode = 2
            refresh = 1
            button_short["BUTTON_X"] = 0
    
    if current_mode == 2:    #enter misc config mode
        if refresh == 1:    #update display
            print("refreshing display")
            picodisplay.set_pen(0, 255, 0)
            picodisplay.clear()                
            picodisplay.set_pen(255, 255, 255)       
            picodisplay.text("BoatMan", 10, 10, 240, 4)
            picodisplay.text("Boat Manager", 10, 40, 240, 2)
            picodisplay.text("Misc Config" , 10, 70, 240, 2)
            picodisplay.text("X: Mode", 10, 100, 240, 2)
            picodisplay.update()
            refresh = 0
        
        if button_short["BUTTON_X"]:    #change mode
            current_mode = 0
            refresh = 1
            button_short["BUTTON_X"] = 0