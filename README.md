Code structure adapted from https://towardsdatascience.com/ultimate-setup-for-your-next-python-project-179bda8a7c2c

Install some tools:
$sudo apt-get install i2c-tools
$sudo apt-get install libopenjp2-7
$sudo apt-get install libatlas-base-dev

To install requirements: $pip3 install -r requirements.txt

Run application: $python3 infodisplay

Connections:

Raspberry Pi            TFT

3V3                     Vcc
GND                     GND
SPIO0 CS (GPIO8)        CS
GPIO25                  RESET
GPIO24                  DC
SPI0 MOSI (GPIO10)      MOSI              
SPI0 SCLK (GPIO11)      SCK
GPIO15                  LED
SPI0 MISO (GPIO0)       MISO
GPIO16                  T_IRQ

                        BME280
3V3                     Vcc
GND                     GND
I2C1 SCL (GPIO3)        SCL
I2C1 SDA (GPIO2)        SDA