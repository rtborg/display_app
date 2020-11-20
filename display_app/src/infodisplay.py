import spidev
from time import sleep, mktime
from datetime import datetime
import RPi.GPIO as GPIO
import signal
from pathlib import Path

from .weather_display import WeatherDisplay
from .hourly_forecast import HourlyForecastDisplay
from .daily_forecast import DailyForecastDisplay
from .lib_tft24T import TFT24T

# GPIO configuration
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# TFT pins
DC = 24
RST = 25
LED = 15
TOUCH_IRQ = 16

# Create TFT LCD/TOUCH object:
TFT = TFT24T(spidev.SpiDev(), GPIO, landscape=False)

# Displays definition
weather_display = WeatherDisplay()
hourly_forecast_display = HourlyForecastDisplay()
daily_forecast_display = DailyForecastDisplay()
images_path = Path(__file__).resolve().parents[1].joinpath('resources/Images')

# Displays are storred in an array and called in infinite loop
dislpays = [weather_display, hourly_forecast_display, daily_forecast_display]

displays_number = len(dislpays)
active_display = 0

# TFT touch interrupt callback
def touch_irq_callback(channel):
    global active_display, displays_number
    active_display = (active_display + 1) % displays_number
    print("Active display: ", active_display)

# Code for graceful shutdown copied from https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


class InfoDisplay():

    @staticmethod
    def run():
        killer = GracefulKiller()

        # Add interrupt handler for the touchscreen
        GPIO.setup(TOUCH_IRQ, GPIO.IN)
        GPIO.add_event_detect(TOUCH_IRQ, edge=GPIO.FALLING, callback=touch_irq_callback, bouncetime=300)

        # Initialize display.
        TFT.initLCD(DC, RST, LED)

        # Get time in seconds
        dti = mktime(datetime.now().timetuple())

        while not killer.kill_now:
            # Get time in seconds and compare it to last timestamp. If a second has expired, 
            # save current timestamp and do stuff
            ndti = mktime(datetime.now().timetuple())
            if dti < ndti:
                dti = ndti

                # Draw current display
                dislpays[active_display].draw(TFT)

                # Sleep to avoid runnign through the loop constantly
                sleep(0.5)
            else:
                sleep(0.01)

        print("Goodbye!")
        TFT.backlite(False)
        TFT.command(0x28)
