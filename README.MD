Reliable control module for boats based on the Raspberry Pi Pico microcontroller and Pimoroni Display Pack written in MicroPython

Pico will need to be running the Pimoroni MicroPython build available here: https://github.com/pimoroni/pimoroni-pico

GPIO is available with the display pack connected, however the PWM slice mapping means only 7 GPIOs are available using the onboard PWM module and this consumes all available UARTs. To have 7 LED PWM outputs and a UART it will be necessary to implement PWM (or UART) in one of the 8 available PIO state machines (not yet done).

See forum thread for details: https://forums.pimoroni.com/t/are-the-unused-gpio-pins-available-with-the-pico-display-pack-firmware-activated/16450/17

Hardware:
3D print case
Raspberry Pi Pico: https://thepihut.com/products/raspberry-pi-pico
Pico Display Pack: https://thepihut.com/products/pico-display-pack
Stacking IO header: https://thepihut.com/products/stacking-header-set-for-raspberry-pi-pico
M3 bolts and nuts: https://www.amazon.co.uk/gp/product/B07PPFT871/ref=ppx_yo_dt_b_asin_title_o02_s00?ie=UTF8&psc=1
MOSFET PWM Drivers: https://www.amazon.co.uk/gp/product/B07QVZK39F/ref=ppx_yo_dt_b_asin_title_o05_s00?ie=UTF8&psc=1