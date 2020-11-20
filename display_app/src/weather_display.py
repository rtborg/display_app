# The WeatherDisplay object shows date, time, current weather, 
# prognosis for next three hours (all from OpenWeatherMap),
# and inside humidity and temperature
# as measured by the bme280 sensor
# The file can be run as a standalone for testing. Go outside the infodisplay directory 
# and issue python3 -m infodisplay.bin.display.weather_display

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
from time import mktime
import RPi.GPIO as GPIO
import spidev

from .display import Display
from .lib_tft24T import TFT24T
from .utils import bme280_get_humidity, bme280_get_temperature, get_weather_data


# Constants for TFT layout
ILI9341_TFTWIDTH = 240
ILI9341_TFTHEIGHT = 320
TOP_MARGIN = 5

# Path to fonts
fonts_path = Path(__file__).resolve().parents[1].joinpath("resources/fonts/")
free_sans_path = str(fonts_path.joinpath("FreeSans.ttf"))

# Fonts
fnt_date = ImageFont.truetype(free_sans_path, 18)
fnt_time = ImageFont.truetype(free_sans_path, 40)
fnt_desc = ImageFont.truetype(free_sans_path, 20)
fnt_temp = ImageFont.truetype(free_sans_path, 35)
fnt_small = ImageFont.truetype(free_sans_path, 15)
fnt_temp_in = ImageFont.truetype(free_sans_path, 30)

# Size constants
FNT_DATE_HEIGHT = fnt_date.getsize("Hello")[1]
FNT_TIME_HEIGHT = fnt_time.getsize("Hello")[1]
FNT_DESC_HEIGHT = fnt_desc.getsize("Hello")[1]
FNT_TEMP_HEIGHT = fnt_temp.getsize("Hello")[1]

CURRENT_DATE_BOX_SIZE = fnt_date.getsize("Day Mon 99 9999")
CURRENT_DATE_X0 = (ILI9341_TFTWIDTH - CURRENT_DATE_BOX_SIZE[0]) // 2
CURRENT_DATE_Y0 = TOP_MARGIN
CURRENT_DATE_X1 = CURRENT_DATE_X0 + CURRENT_DATE_BOX_SIZE[0]
CURRENT_DATE_Y1 = CURRENT_DATE_Y0 + CURRENT_DATE_BOX_SIZE[1]
CURRENT_DATE_COORDS = (CURRENT_DATE_X0, CURRENT_DATE_Y0, CURRENT_DATE_X1, CURRENT_DATE_Y1)

CURRENT_TIME_BOX_SIZE = fnt_time.getsize("99:99:99")
CURRENT_TIME_X0 = (ILI9341_TFTWIDTH - CURRENT_TIME_BOX_SIZE[0]) // 2
CURRENT_TIME_Y0 = CURRENT_DATE_Y1 
CURRENT_TIME_X1 = CURRENT_TIME_X0 + CURRENT_TIME_BOX_SIZE[0]
CURRENT_TIME_Y1 = CURRENT_TIME_Y0 + CURRENT_TIME_BOX_SIZE[1]
CURRENT_TIME_COORDS = (CURRENT_TIME_X0, CURRENT_TIME_Y0, CURRENT_TIME_X1, CURRENT_TIME_Y1)

CURRENT_WEATHER_ICON_Y0 = TOP_MARGIN + FNT_DATE_HEIGHT + \
    TOP_MARGIN + FNT_TIME_HEIGHT + TOP_MARGIN
CURRENT_WEATHER_ICON_Y1 = CURRENT_WEATHER_ICON_Y0 + 100
CURRENT_WEATHER_ICON_X0 = 0
CURRENT_WEATHER_ICON_X1 = CURRENT_WEATHER_ICON_X0 + 100

WEATHER_DESCRIPTION_X0 = CURRENT_WEATHER_ICON_X1
WEATHER_DESCRIPTION_X1 = ILI9341_TFTWIDTH
WEATHER_DESCRIPTION_Y0 = CURRENT_WEATHER_ICON_Y0
WEATHER_DESCRIPTION_Y1 = WEATHER_DESCRIPTION_Y0 + FNT_DESC_HEIGHT
WEATHER_DESCRIPTION_BOX_SIZE = (
    (WEATHER_DESCRIPTION_X1 - WEATHER_DESCRIPTION_X0), (FNT_DESC_HEIGHT))
WEATHER_DESCRIPTION_COORDS = (WEATHER_DESCRIPTION_X0, WEATHER_DESCRIPTION_Y0, WEATHER_DESCRIPTION_X1, WEATHER_DESCRIPTION_Y1)

HUMIDITY_X0 = CURRENT_WEATHER_ICON_X1
HUMIDITY_Y0 = WEATHER_DESCRIPTION_Y1 + 2
HUMIDITY_X1 = ILI9341_TFTWIDTH
HUMIDITY_Y1 = HUMIDITY_Y0 + FNT_DESC_HEIGHT
HUMIDITY_BOX_SIZE = ((HUMIDITY_X1 - HUMIDITY_X0), FNT_DESC_HEIGHT)
HUMIDITY_COORDS = (HUMIDITY_X0, HUMIDITY_Y0, HUMIDITY_X1, HUMIDITY_Y1)

WINDSPEED_X0 = CURRENT_WEATHER_ICON_X1
WINDSPEED_Y0 = HUMIDITY_Y1 + 2
WINDSPEED_X1 = ILI9341_TFTWIDTH
WINDSPEED_Y1 = WINDSPEED_Y0 + FNT_DESC_HEIGHT
WINDSPEED_BOX_SIZE = ((WINDSPEED_X1 - WINDSPEED_X0), FNT_DESC_HEIGHT)
WINDSPEED_COORDS = (WINDSPEED_X0, WINDSPEED_Y0, WINDSPEED_X1, WINDSPEED_Y1) 

TEMPERATURE_X0 = CURRENT_WEATHER_ICON_X1
TEMPERATURE_Y0 = WINDSPEED_Y1 + 2
TEMPERATURE_X1 = ILI9341_TFTWIDTH
TEMPERATURE_Y1 = TEMPERATURE_Y0 + FNT_TEMP_HEIGHT
TEMPERATURE_BOX_SIZE = ((TEMPERATURE_X1 - TEMPERATURE_X0), FNT_TEMP_HEIGHT)
TEMPERATURE_COORDS = (TEMPERATURE_X0, TEMPERATURE_Y0, TEMPERATURE_X1, TEMPERATURE_Y1)

HOURLY_TIME_BOX_SIZE = fnt_small.getsize("00:00")
HOURLY_TIME_GAP = (ILI9341_TFTWIDTH - (3 * HOURLY_TIME_BOX_SIZE[0])) // 4

HOURLY_TIME_1_X0 = HOURLY_TIME_GAP
HOURLY_TIME_1_Y0 = TEMPERATURE_Y1 + TOP_MARGIN
HOURLY_TIME_1_X1 = HOURLY_TIME_1_X0 + HOURLY_TIME_BOX_SIZE[0]
HOURLY_TIME_1_Y1 = HOURLY_TIME_1_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_1_COORDS = (HOURLY_TIME_1_X0, HOURLY_TIME_1_Y0, HOURLY_TIME_1_X1, HOURLY_TIME_1_Y1)

HOURLY_TIME_2_X0 = HOURLY_TIME_1_X1 + HOURLY_TIME_GAP
HOURLY_TIME_2_YO = TEMPERATURE_Y1 + TOP_MARGIN
HOURLY_TIME_2_X1 = HOURLY_TIME_2_X0 + HOURLY_TIME_BOX_SIZE[0]
HOURLY_TIME_2_Y1 = HOURLY_TIME_2_YO + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_2_COORDS = (HOURLY_TIME_2_X0, HOURLY_TIME_2_YO, HOURLY_TIME_2_X1, HOURLY_TIME_2_Y1)

HOURLY_TIME_3_X0 = HOURLY_TIME_2_X1 + HOURLY_TIME_GAP
HOURLY_TIME_3_YO = TEMPERATURE_Y1 + TOP_MARGIN
HOURLY_TIME_3_X1 = HOURLY_TIME_3_X0 + HOURLY_TIME_BOX_SIZE[0]
HOURLY_TIME_3_Y1 = HOURLY_TIME_3_YO + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_3_COORDS = (HOURLY_TIME_3_X0, HOURLY_TIME_3_YO, HOURLY_TIME_3_X1, HOURLY_TIME_3_Y1)

HOURLY_TEMP_BOX_SIZE = fnt_small.getsize("99.9\u00b0C")
HOURLY_TEMP_GAP = (ILI9341_TFTWIDTH - (3 * HOURLY_TEMP_BOX_SIZE[0]))  // 4

HOURLY_TEMP_1_X0 = HOURLY_TEMP_GAP
HOURLY_TEMP_1_Y0 = HOURLY_TIME_1_Y1 + 2
HOURLY_TEMP_1_X1 = HOURLY_TEMP_1_X0 + HOURLY_TEMP_BOX_SIZE[0]
HOURLY_TEMP_1_Y1 = HOURLY_TEMP_1_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_1_COORDS = (HOURLY_TEMP_1_X0, HOURLY_TEMP_1_Y0, HOURLY_TEMP_1_X1, HOURLY_TEMP_1_Y1)

HOURLY_TEMP_2_X0 = HOURLY_TEMP_1_X1 + HOURLY_TEMP_GAP
HOURLY_TEMP_2_Y0 = HOURLY_TIME_1_Y1 + 2
HOURLY_TEMP_2_X1 = HOURLY_TEMP_2_X0 + HOURLY_TEMP_BOX_SIZE[0]
HOURLY_TEMP_2_Y1 = HOURLY_TEMP_2_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_2_COORDS = (HOURLY_TEMP_2_X0, HOURLY_TEMP_2_Y0, HOURLY_TEMP_2_X1, HOURLY_TEMP_2_Y1)

HOURLY_TEMP_3_X0 = HOURLY_TEMP_2_X1 + HOURLY_TEMP_GAP
HOURLY_TEMP_3_Y0 = HOURLY_TIME_1_Y1 + 2
HOURLY_TEMP_3_X1 = HOURLY_TEMP_3_X0 + HOURLY_TEMP_BOX_SIZE[0]
HOURLY_TEMP_3_Y1 = HOURLY_TEMP_3_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_3_COORDS = (HOURLY_TEMP_3_X0, HOURLY_TEMP_3_Y0, HOURLY_TEMP_3_X1, HOURLY_TEMP_3_Y1)

HOURLY_ICON_1_X0 = 22
HOURLY_ICON_1_Y0 = HOURLY_TEMP_3_Y1 + 2
HOURLY_ICON_1_X1 = HOURLY_ICON_1_X0 + 50
HOURLY_ICON_1_Y1 = HOURLY_ICON_1_Y0 + 50

HOURLY_ICON_2_X0 = HOURLY_ICON_1_X1 + 23
HOURLY_ICON_2_Y0 = HOURLY_TEMP_3_Y1 + 2
HOURLY_ICON_2_X1 = HOURLY_ICON_2_X0 + 50
HOURLY_ICON_2_Y1 = HOURLY_ICON_2_Y0 + 50

HOURLY_ICON_3_X0 = HOURLY_ICON_2_X1 + 23
HOURLY_ICON_3_Y0 = HOURLY_TEMP_3_Y1 + 2
HOURLY_ICON_3_X1 = HOURLY_ICON_3_X0 + 50
HOURLY_ICON_3_Y1 = HOURLY_ICON_3_Y0 + 50

HOURLY_HUMIDITY_BOX_SIZE = fnt_small.getsize("99.9%")
HOURLY_HUMIDITY_GAP = (ILI9341_TFTWIDTH - (3 * HOURLY_HUMIDITY_BOX_SIZE[0])) // 4

HOURLY_HUMIDITY_1_X0 = HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_1_Y0 = HOURLY_ICON_1_Y1
HOURLY_HUMIDITY_1_X1 = HOURLY_HUMIDITY_1_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_1_Y1 = HOURLY_HUMIDITY_1_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_1_COORDS = (HOURLY_HUMIDITY_1_X0, HOURLY_HUMIDITY_1_Y0, HOURLY_HUMIDITY_1_X1, HOURLY_HUMIDITY_1_Y1)

HOURLY_HUMIDITY_2_X0 = HOURLY_HUMIDITY_1_X1 + HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_2_Y0 = HOURLY_ICON_1_Y1
HOURLY_HUMIDITY_2_X1 = HOURLY_HUMIDITY_2_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_2_Y1 = HOURLY_HUMIDITY_2_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_2_COORDS = (HOURLY_HUMIDITY_2_X0, HOURLY_HUMIDITY_2_Y0, HOURLY_HUMIDITY_2_X1, HOURLY_HUMIDITY_2_Y1)

HOURLY_HUMIDITY_3_X0 = HOURLY_HUMIDITY_2_X1 + HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_3_Y0 = HOURLY_ICON_1_Y1
HOURLY_HUMIDITY_3_X1 = HOURLY_HUMIDITY_3_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_3_Y1 = HOURLY_HUMIDITY_3_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_3_COORDS = (HOURLY_HUMIDITY_3_X0, HOURLY_HUMIDITY_3_Y0, HOURLY_HUMIDITY_3_X1, HOURLY_HUMIDITY_3_Y1)

INSIDE_TEMP_BOX_SIZE = fnt_temp_in.getsize("99.9\u00b0C")
INSIDE_TEMP_X0 = 10
INSIDE_TEMP_Y0 = HOURLY_HUMIDITY_1_Y1 + 20
INSIDE_TEMP_X1 = INSIDE_TEMP_X0 + INSIDE_TEMP_BOX_SIZE[0]
INSIDE_TEMP_Y1 = INSIDE_TEMP_Y0 + INSIDE_TEMP_BOX_SIZE[1]
INSIDE_TEMP_COORDS = (INSIDE_TEMP_X0, INSIDE_TEMP_Y0, INSIDE_TEMP_X1, INSIDE_TEMP_Y1)

INSIDE_HUMIDITY_BOX_SIZE = fnt_temp_in.getsize("99.9%")
INSIDE_HUMIDITY_X0 = ILI9341_TFTWIDTH - INSIDE_HUMIDITY_BOX_SIZE[0] - 10
INSIDE_HUMIDITY_Y0 = INSIDE_TEMP_Y0
INSIDE_HUMIDITY_X1 = INSIDE_HUMIDITY_X0 + INSIDE_HUMIDITY_BOX_SIZE[0]
INSIDE_HUMIDITY_Y1 = INSIDE_HUMIDITY_Y0 + INSIDE_HUMIDITY_BOX_SIZE[1] 
INSIDE_HUMIDITY_COORDS = (INSIDE_HUMIDITY_X0, INSIDE_HUMIDITY_Y0, INSIDE_HUMIDITY_X1, INSIDE_HUMIDITY_Y1)

pink = (255, 102, 255)
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)
light_blue = (191, 253, 255)


# The WeatherDisplay draws time and weather on the TFT

class WeatherDisplay(Display):

    def __init__(self, lat=54.9981, lon=-7.3093):
        self.lat = lat
        self.lon = lon
        self.weather = get_weather_data(self.lat, self.lon)
        # Get timestamp in seconds 
        self.time = mktime(datetime.now().timetuple())
        self._has_drawn_display = False

    def _tft_print_blocktext(self, TFT, text, font, boxsize, coordinates, fill_color='black', font_color='white'):
        bounding_box = Image.new('RGB', boxsize, fill_color)
        draw = ImageDraw.Draw(bounding_box)
        draw.text((0,0), text, font=font, fill=font_color)
        TFT.display_block(bounding_box, coordinates[0], coordinates[1], coordinates[2]-1, coordinates[3]-1)

    def _print_current_date(self, TFT, timestamp):
        current_date = timestamp.strftime("%a %d %b %Y")
        self._tft_print_blocktext(TFT, current_date, fnt_date, CURRENT_DATE_BOX_SIZE, CURRENT_DATE_COORDS)

    def _print_current_time(self, TFT, timestamp):
        current_time = timestamp.strftime("%H:%M:%S")
        self._tft_print_blocktext(TFT, current_time, fnt_time, CURRENT_TIME_BOX_SIZE, CURRENT_TIME_COORDS)

    def _print_current_weather(self, TFT, weather):
        try:
            temp = weather["current"]["temp"]
            feels_like = weather["current"]["feels_like"]
            humidity = weather["current"]["humidity"]
            description = weather["current"]["weather"][0]["main"]
            description = description.title()
            wind_speed = weather["current"]["wind_speed"]
            icon = weather["current"]["weather"][0]["icon"]

            # Get and display icon for current weather
            with Image.open(Path(__file__).resolve().parents[1].joinpath("resources/LargeIcons/" + icon + ".bmp")) as current_weather_icon:
                TFT.display_block(current_weather_icon, CURRENT_WEATHER_ICON_X0,
                                CURRENT_WEATHER_ICON_Y0, CURRENT_WEATHER_ICON_X1-1, CURRENT_WEATHER_ICON_Y1-1)

            # Display description
            self._tft_print_blocktext(TFT, description, fnt_desc, WEATHER_DESCRIPTION_BOX_SIZE, WEATHER_DESCRIPTION_COORDS, fill_color='black', font_color='yellow')

            # Display humidity
            humidity_string = f"{humidity:<4.1f}%"
            self._tft_print_blocktext(TFT, humidity_string, fnt_desc, HUMIDITY_BOX_SIZE, HUMIDITY_COORDS, font_color=light_blue)

            # Display wind speed
            windspeed_string = f"{wind_speed:<4.2f} m/s"
            self._tft_print_blocktext(TFT, windspeed_string, fnt_desc, WINDSPEED_BOX_SIZE, WINDSPEED_COORDS)

            # Display current temperature
            temp_string = f"{temp:<4.1f}\u00b0C"
            self._tft_print_blocktext(TFT, temp_string, fnt_temp, TEMPERATURE_BOX_SIZE, TEMPERATURE_COORDS)

        except Exception as ex:
            print("An exception ocurred while parsing weather", ex)

    def _print_hourly_forecast(self, TFT, weather):
        try:
            # For 3 hours, get time, temperature, icon, humidity
            hour_one = weather["hourly"][1]
            hour_one_time = datetime.utcfromtimestamp(hour_one["dt"]).strftime("%H:%M")
            hour_one_temp = hour_one["temp"]
            hour_one_humidity = hour_one["humidity"]
            hour_one_icon_id = hour_one["weather"][0]["icon"]

            hour_two = weather["hourly"][2]
            hour_two_time = datetime.utcfromtimestamp(hour_two["dt"]).strftime("%H:%M")
            hour_two_temp = hour_two["temp"]
            hour_two_humidity = hour_two["humidity"]
            hour_two_icon_id = hour_two["weather"][0]["icon"]

            hour_three = weather["hourly"][3]
            hour_three_time = datetime.utcfromtimestamp(hour_three["dt"]).strftime("%H:%M")
            hour_three_temp = hour_three["temp"]
            hour_three_humidity = hour_three["humidity"]
            hour_three_icon_id = hour_three["weather"][0]["icon"]

            self._tft_print_blocktext(TFT, hour_one_time, fnt_small, HOURLY_TIME_BOX_SIZE, HOURLY_TIME_1_COORDS)
            self._tft_print_blocktext(TFT, hour_two_time, fnt_small, HOURLY_TIME_BOX_SIZE, HOURLY_TIME_2_COORDS)
            self._tft_print_blocktext(TFT, hour_three_time, fnt_small, HOURLY_TIME_BOX_SIZE, HOURLY_TIME_3_COORDS)

            h1_temp_string = f"{hour_one_temp:>4.1f}\u00b0C"
            h2_temp_string = f"{hour_two_temp:>4.1f}\u00b0C"
            h3_temp_string = f"{hour_three_temp:>4.1f}\u00b0C"

            self._tft_print_blocktext(TFT, h1_temp_string, fnt_small, HOURLY_TEMP_BOX_SIZE, HOURLY_TEMP_1_COORDS)
            self._tft_print_blocktext(TFT, h2_temp_string, fnt_small, HOURLY_TEMP_BOX_SIZE, HOURLY_TEMP_2_COORDS)
            self._tft_print_blocktext(TFT, h3_temp_string, fnt_small, HOURLY_TEMP_BOX_SIZE, HOURLY_TEMP_3_COORDS)

            # Path(__file__).resolve().parents[1].joinpath("resources/SmallIcons/" + hour_one_icon_id + ".bmp")
            with Image.open(Path(__file__).resolve().parents[1].joinpath("resources/SmallIcons/" + hour_one_icon_id + ".bmp")) as hour_one_icon:
                TFT.display_block(hour_one_icon, HOURLY_ICON_1_X0, HOURLY_ICON_1_Y0, HOURLY_ICON_1_X1-1, HOURLY_ICON_1_Y1-1)
            
            with Image.open(Path(__file__).resolve().parents[1].joinpath("resources/SmallIcons/" + hour_two_icon_id + ".bmp")) as hour_two_icon:
                TFT.display_block(hour_two_icon, HOURLY_ICON_2_X0, HOURLY_ICON_2_Y0, HOURLY_ICON_2_X1-1, HOURLY_ICON_2_Y1-1)

            with Image.open(Path(__file__).resolve().parents[1].joinpath("resources/SmallIcons/" + hour_three_icon_id + ".bmp")) as hour_three_icon:
                TFT.display_block(hour_three_icon, HOURLY_ICON_3_X0, HOURLY_ICON_3_Y0, HOURLY_ICON_3_X1-1, HOURLY_ICON_3_Y1-1)

            h1_humidity_string = f"{hour_one_humidity:4.1f}%"
            h2_humidity_string = f"{hour_two_humidity:4.1f}%"
            h3_humidity_string = f"{hour_three_humidity:4.1f}%"

            self._tft_print_blocktext(TFT, h1_humidity_string, fnt_small, HOURLY_HUMIDITY_BOX_SIZE, HOURLY_HUMIDITY_1_COORDS, font_color=light_blue)
            self._tft_print_blocktext(TFT, h2_humidity_string, fnt_small, HOURLY_HUMIDITY_BOX_SIZE, HOURLY_HUMIDITY_2_COORDS, font_color=light_blue)
            self._tft_print_blocktext(TFT, h3_humidity_string, fnt_small, HOURLY_HUMIDITY_BOX_SIZE, HOURLY_HUMIDITY_3_COORDS, font_color=light_blue)

        except Exception as ex:
            print("An exception ocurred while parsing weather", ex)

    def _print_bme280_data(self, TFT):
        in_temp = bme280_get_temperature()
        in_himidity = bme280_get_humidity()
        in_temp_string = f"{in_temp:>4.1f}\u00b0C"
        in_humidity_string = f"{in_himidity:4.1f}%"
        self._tft_print_blocktext(TFT, in_temp_string, fnt_temp_in, INSIDE_TEMP_BOX_SIZE, INSIDE_TEMP_COORDS)
        self._tft_print_blocktext(TFT, in_humidity_string, fnt_temp_in, INSIDE_HUMIDITY_BOX_SIZE, INSIDE_HUMIDITY_COORDS, font_color=light_blue)


    def _draw_complete_display(self, TFT):
        now = datetime.now()

        TFT.clear(black)
        self._print_current_date(TFT, now)
        self._print_current_time(TFT, now)

        if self.weather is not None:
            try:
                weather_timestamp = datetime.utcfromtimestamp(self.weather["current"]["dt"])
                tdiff = now - weather_timestamp
                if tdiff.seconds >= 120:
                    self.weather = get_weather_data(self.lat, self.lon)
                   
                # Get weather data and update display
                self._print_current_weather(TFT, self.weather)
                self._print_hourly_forecast(TFT, self.weather)
                self._print_bme280_data(TFT)
            except Exception as ex:
                print(ex)      

    def _update_display(self, TFT):
        now = datetime.now()
        self._print_current_time(TFT, now)

        if (now.second == 0 and now.minute == 0):
            self._print_current_date(TFT, now)

        # Get weather data every 2 minutes
        if (now.second == 0 and now.minute % 2 == 0):
            self.weather = get_weather_data(self.lat, self.lon)
            if self.weather is not None:
                self._print_current_weather(TFT, self.weather)
                self._print_hourly_forecast(TFT, self.weather)
                self._print_bme280_data(TFT)
            else:
                print("Could not validate weather data json.", self.weather)

    # Draw the complete display
    def draw(self, TFT):
        now = mktime(datetime.now().timetuple())

        if (now - self.time > 2) or not self._has_drawn_display:
            self.time = now
            self._draw_complete_display(TFT)
            self._has_drawn_display = True
        else:
            self.time = now
            self._update_display(TFT)





if __name__ == '__main__':
    print("Fetching weather data and printing it on thr TFT...")
    print("CTRL+C for exit.")

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Raspberry Pi configuration.
    # For LCD TFT SCREEN:
    DC = 24
    RST = 25
    LED = 15

    # Create TFT LCD/TOUCH object:
    TFTDisplay = TFT24T(spidev.SpiDev(), GPIO, landscape=False)
    # If landscape=False or omitted, display defaults to portrait mode

    # Initialize display.
    TFTDisplay.initLCD(DC, RST, LED)

    weatherDisplay = WeatherDisplay()
    weatherDisplay.draw(TFTDisplay)

    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Interrupted. Goodbye!")
        TFTDisplay.backlite(False)
        TFTDisplay.command(0x28)