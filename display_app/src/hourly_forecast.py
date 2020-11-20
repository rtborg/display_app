from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from datetime import datetime
from time import mktime

from .display import Display
from .utils import get_weather_data


# Constants for TFT layout
ILI9341_TFTWIDTH = 240
ILI9341_TFTHEIGHT = 320
ICON_HEIGHT = 50
ICON_WIDTH = 50
TOP_MARGIN = 5

# Path to fonts
fonts_path = Path(__file__).resolve().parents[1].joinpath("resources/fonts/")
free_sans_path = str(fonts_path.joinpath("FreeSans.ttf"))

# Fonts
fnt_small = ImageFont.truetype(free_sans_path, 15)
fnt_large = ImageFont.truetype(free_sans_path, 16)

# Box sizes for text
HOURLY_TIME_BOX_SIZE = fnt_small.getsize("00:00")
HOURLY_TIME_GAP = (ILI9341_TFTWIDTH - (3 * HOURLY_TIME_BOX_SIZE[0])) // 4

HOURLY_TEMP_BOX_SIZE = fnt_small.getsize("99.9\u00b0C")
HOURLY_TEMP_GAP = (ILI9341_TFTWIDTH - (3 * HOURLY_TEMP_BOX_SIZE[0]))  // 4

HOURLY_HUMIDITY_BOX_SIZE = fnt_small.getsize("99.9%")
HOURLY_HUMIDITY_GAP = (ILI9341_TFTWIDTH - (3 * HOURLY_HUMIDITY_BOX_SIZE[0])) // 4

# Coordinates for row 1
HOURLY_TIME_1_X0 = HOURLY_TIME_GAP
HOURLY_TIME_1_Y0 = 5
HOURLY_TIME_1_X1 = HOURLY_TIME_1_X0 + HOURLY_TIME_BOX_SIZE[0]
HOURLY_TIME_1_Y1 = HOURLY_TIME_1_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_1_COORDS = (HOURLY_TIME_1_X0, HOURLY_TIME_1_Y0, HOURLY_TIME_1_X1, HOURLY_TIME_1_Y1)

HOURLY_TIME_2_X0 = HOURLY_TIME_1_X1 + HOURLY_TIME_GAP
HOURLY_TIME_2_YO = HOURLY_TIME_1_Y0
HOURLY_TIME_2_X1 = HOURLY_TIME_2_X0 + HOURLY_TIME_BOX_SIZE[0]
HOURLY_TIME_2_Y1 = HOURLY_TIME_2_YO + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_2_COORDS = (HOURLY_TIME_2_X0, HOURLY_TIME_2_YO, HOURLY_TIME_2_X1, HOURLY_TIME_2_Y1)

HOURLY_TIME_3_X0 = HOURLY_TIME_2_X1 + HOURLY_TIME_GAP
HOURLY_TIME_3_YO = HOURLY_TIME_1_Y0
HOURLY_TIME_3_X1 = HOURLY_TIME_3_X0 + HOURLY_TIME_BOX_SIZE[0]
HOURLY_TIME_3_Y1 = HOURLY_TIME_3_YO + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_3_COORDS = (HOURLY_TIME_3_X0, HOURLY_TIME_3_YO, HOURLY_TIME_3_X1, HOURLY_TIME_3_Y1)

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
ICON_1_COORDS = (HOURLY_ICON_1_X0, HOURLY_ICON_1_Y0, HOURLY_ICON_1_X1-1, HOURLY_ICON_1_Y1-1)

HOURLY_ICON_2_X0 = HOURLY_ICON_1_X1 + 23
HOURLY_ICON_2_Y0 = HOURLY_TEMP_3_Y1 + 2
HOURLY_ICON_2_X1 = HOURLY_ICON_2_X0 + 50
HOURLY_ICON_2_Y1 = HOURLY_ICON_2_Y0 + 50
ICON_2_COORDS = (HOURLY_ICON_2_X0, HOURLY_ICON_2_Y0, HOURLY_ICON_2_X1-1, HOURLY_ICON_2_Y1-1)

HOURLY_ICON_3_X0 = HOURLY_ICON_2_X1 + 23
HOURLY_ICON_3_Y0 = HOURLY_TEMP_3_Y1 + 2
HOURLY_ICON_3_X1 = HOURLY_ICON_3_X0 + 50
HOURLY_ICON_3_Y1 = HOURLY_ICON_3_Y0 + 50
ICON_3_COORDS = (HOURLY_ICON_3_X0, HOURLY_ICON_3_Y0, HOURLY_ICON_3_X1-1, HOURLY_ICON_3_Y1-1)

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

# Coordinates for row 2
HOURLY_TIME_4_X0 = HOURLY_TIME_1_X0
HOURLY_TIME_4_Y0 = HOURLY_HUMIDITY_1_Y1 + 10
HOURLY_TIME_4_X1 = HOURLY_TIME_1_X1
HOURLY_TIME_4_Y1 = HOURLY_TIME_4_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_4_COORDS = (HOURLY_TIME_4_X0, HOURLY_TIME_4_Y0, HOURLY_TIME_4_X1, HOURLY_TIME_4_Y1)

HOURLY_TIME_5_X0 = HOURLY_TIME_2_X0
HOURLY_TIME_5_Y0 = HOURLY_HUMIDITY_1_Y1 + 10
HOURLY_TIME_5_X1 = HOURLY_TIME_2_X1
HOURLY_TIME_5_Y1 = HOURLY_TIME_5_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_5_COORDS = (HOURLY_TIME_5_X0, HOURLY_TIME_5_Y0, HOURLY_TIME_5_X1, HOURLY_TIME_5_Y1)

HOURLY_TIME_6_X0 = HOURLY_TIME_3_X0
HOURLY_TIME_6_Y0 = HOURLY_HUMIDITY_1_Y1 + 10
HOURLY_TIME_6_X1 = HOURLY_TIME_3_X1
HOURLY_TIME_6_Y1 = HOURLY_TIME_6_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_6_COORDS = (HOURLY_TIME_6_X0, HOURLY_TIME_6_Y0, HOURLY_TIME_6_X1, HOURLY_TIME_6_Y1)

HOURLY_TEMP_4_X0 = HOURLY_TEMP_1_X0
HOURLY_TEMP_4_Y0 = HOURLY_TIME_4_Y1 + 2
HOURLY_TEMP_4_X1 = HOURLY_TEMP_1_X1
HOURLY_TEMP_4_Y1 = HOURLY_TEMP_4_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_4_COORDS = (HOURLY_TEMP_4_X0, HOURLY_TEMP_4_Y0, HOURLY_TEMP_4_X1, HOURLY_TEMP_4_Y1)

HOURLY_TEMP_5_X0 = HOURLY_TEMP_2_X0
HOURLY_TEMP_5_Y0 = HOURLY_TIME_4_Y1 + 2
HOURLY_TEMP_5_X1 = HOURLY_TEMP_2_X1
HOURLY_TEMP_5_Y1 = HOURLY_TEMP_5_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_5_COORDS = (HOURLY_TEMP_5_X0, HOURLY_TEMP_5_Y0, HOURLY_TEMP_5_X1, HOURLY_TEMP_5_Y1)

HOURLY_TEMP_6_X0 = HOURLY_TEMP_3_X0
HOURLY_TEMP_6_Y0 = HOURLY_TIME_6_Y1 + 2
HOURLY_TEMP_6_X1 = HOURLY_TEMP_3_X1
HOURLY_TEMP_6_Y1 = HOURLY_TEMP_6_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_6_COORDS = (HOURLY_TEMP_6_X0, HOURLY_TEMP_6_Y0, HOURLY_TEMP_6_X1, HOURLY_TEMP_6_Y1)

HOURLY_ICON_4_X0 = 22
HOURLY_ICON_4_Y0 = HOURLY_TEMP_4_Y1 + 2
HOURLY_ICON_4_X1 = HOURLY_ICON_4_X0 + 50
HOURLY_ICON_4_Y1 = HOURLY_ICON_4_Y0 + 50
ICON_4_COORDS = (HOURLY_ICON_4_X0, HOURLY_ICON_4_Y0, HOURLY_ICON_4_X1-1, HOURLY_ICON_4_Y1-1)

HOURLY_ICON_5_X0 = HOURLY_ICON_4_X1 + 23
HOURLY_ICON_5_Y0 = HOURLY_TEMP_5_Y1 + 2
HOURLY_ICON_5_X1 = HOURLY_ICON_5_X0 + 50
HOURLY_ICON_5_Y1 = HOURLY_ICON_5_Y0 + 50
ICON_5_COORDS = (HOURLY_ICON_5_X0, HOURLY_ICON_5_Y0, HOURLY_ICON_5_X1-1, HOURLY_ICON_5_Y1-1)

HOURLY_ICON_6_X0 = HOURLY_ICON_5_X1 + 23
HOURLY_ICON_6_Y0 = HOURLY_TEMP_6_Y1 + 2
HOURLY_ICON_6_X1 = HOURLY_ICON_6_X0 + 50
HOURLY_ICON_6_Y1 = HOURLY_ICON_6_Y0 + 50
ICON_6_COORDS = (HOURLY_ICON_6_X0, HOURLY_ICON_6_Y0, HOURLY_ICON_6_X1-1, HOURLY_ICON_6_Y1-1)

HOURLY_HUMIDITY_4_X0 = HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_4_Y0 = HOURLY_ICON_4_Y1
HOURLY_HUMIDITY_4_X1 = HOURLY_HUMIDITY_4_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_4_Y1 = HOURLY_HUMIDITY_4_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_4_COORDS = (HOURLY_HUMIDITY_4_X0, HOURLY_HUMIDITY_4_Y0, HOURLY_HUMIDITY_4_X1, HOURLY_HUMIDITY_4_Y1)

HOURLY_HUMIDITY_5_X0 = HOURLY_HUMIDITY_4_X1 + HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_5_Y0 = HOURLY_ICON_5_Y1
HOURLY_HUMIDITY_5_X1 = HOURLY_HUMIDITY_5_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_5_Y1 = HOURLY_HUMIDITY_5_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_5_COORDS = (HOURLY_HUMIDITY_5_X0, HOURLY_HUMIDITY_5_Y0, HOURLY_HUMIDITY_5_X1, HOURLY_HUMIDITY_5_Y1)

HOURLY_HUMIDITY_6_X0 = HOURLY_HUMIDITY_5_X1 + HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_6_Y0 = HOURLY_ICON_6_Y1
HOURLY_HUMIDITY_6_X1 = HOURLY_HUMIDITY_6_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_6_Y1 = HOURLY_HUMIDITY_6_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_6_COORDS = (HOURLY_HUMIDITY_6_X0, HOURLY_HUMIDITY_6_Y0, HOURLY_HUMIDITY_6_X1, HOURLY_HUMIDITY_6_Y1)

# Coordinates for row 3
HOURLY_TIME_7_X0 = HOURLY_TIME_1_X0
HOURLY_TIME_7_Y0 = HOURLY_HUMIDITY_4_Y1 + 10
HOURLY_TIME_7_X1 = HOURLY_TIME_1_X1
HOURLY_TIME_7_Y1 = HOURLY_TIME_7_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_7_COORDS = (HOURLY_TIME_7_X0, HOURLY_TIME_7_Y0, HOURLY_TIME_7_X1, HOURLY_TIME_7_Y1)

HOURLY_TIME_8_X0 = HOURLY_TIME_2_X0
HOURLY_TIME_8_Y0 = HOURLY_HUMIDITY_5_Y1 + 10
HOURLY_TIME_8_X1 = HOURLY_TIME_2_X1
HOURLY_TIME_8_Y1 = HOURLY_TIME_8_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_8_COORDS = (HOURLY_TIME_8_X0, HOURLY_TIME_8_Y0, HOURLY_TIME_8_X1, HOURLY_TIME_8_Y1)

HOURLY_TIME_9_X0 = HOURLY_TIME_3_X0
HOURLY_TIME_9_Y0 = HOURLY_HUMIDITY_6_Y1 + 10
HOURLY_TIME_9_X1 = HOURLY_TIME_3_X1
HOURLY_TIME_9_Y1 = HOURLY_TIME_9_Y0 + HOURLY_TIME_BOX_SIZE[1]
HOURLY_TIME_9_COORDS = (HOURLY_TIME_9_X0, HOURLY_TIME_9_Y0, HOURLY_TIME_9_X1, HOURLY_TIME_9_Y1)

HOURLY_TEMP_7_X0 = HOURLY_TEMP_1_X0
HOURLY_TEMP_7_Y0 = HOURLY_TIME_7_Y1 + 2
HOURLY_TEMP_7_X1 = HOURLY_TEMP_1_X1
HOURLY_TEMP_7_Y1 = HOURLY_TEMP_7_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_7_COORDS = (HOURLY_TEMP_7_X0, HOURLY_TEMP_7_Y0, HOURLY_TEMP_7_X1, HOURLY_TEMP_7_Y1)

HOURLY_TEMP_8_X0 = HOURLY_TEMP_2_X0
HOURLY_TEMP_8_Y0 = HOURLY_TIME_8_Y1 + 2
HOURLY_TEMP_8_X1 = HOURLY_TEMP_2_X1
HOURLY_TEMP_8_Y1 = HOURLY_TEMP_8_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_8_COORDS = (HOURLY_TEMP_8_X0, HOURLY_TEMP_8_Y0, HOURLY_TEMP_8_X1, HOURLY_TEMP_8_Y1)

HOURLY_TEMP_9_X0 = HOURLY_TEMP_3_X0
HOURLY_TEMP_9_Y0 = HOURLY_TIME_9_Y1 + 2
HOURLY_TEMP_9_X1 = HOURLY_TEMP_3_X1
HOURLY_TEMP_9_Y1 = HOURLY_TEMP_9_Y0 + HOURLY_TEMP_BOX_SIZE[1]
HOURLY_TEMP_9_COORDS = (HOURLY_TEMP_9_X0, HOURLY_TEMP_9_Y0, HOURLY_TEMP_9_X1, HOURLY_TEMP_9_Y1)

HOURLY_ICON_7_X0 = 22
HOURLY_ICON_7_Y0 = HOURLY_TEMP_7_Y1 + 2
HOURLY_ICON_7_X1 = HOURLY_ICON_7_X0 + 50
HOURLY_ICON_7_Y1 = HOURLY_ICON_7_Y0 + 50
ICON_7_COORDS = (HOURLY_ICON_7_X0, HOURLY_ICON_7_Y0, HOURLY_ICON_7_X1-1, HOURLY_ICON_7_Y1-1)

HOURLY_ICON_8_X0 = HOURLY_ICON_7_X1 + 23
HOURLY_ICON_8_Y0 = HOURLY_TEMP_8_Y1 + 2
HOURLY_ICON_8_X1 = HOURLY_ICON_8_X0 + 50
HOURLY_ICON_8_Y1 = HOURLY_ICON_8_Y0 + 50
ICON_8_COORDS = (HOURLY_ICON_8_X0, HOURLY_ICON_8_Y0, HOURLY_ICON_8_X1-1, HOURLY_ICON_8_Y1-1)

HOURLY_ICON_9_X0 = HOURLY_ICON_8_X1 + 23
HOURLY_ICON_9_Y0 = HOURLY_TEMP_9_Y1 + 2
HOURLY_ICON_9_X1 = HOURLY_ICON_9_X0 + 50
HOURLY_ICON_9_Y1 = HOURLY_ICON_9_Y0 + 50
ICON_9_COORDS = (HOURLY_ICON_9_X0, HOURLY_ICON_9_Y0, HOURLY_ICON_9_X1-1, HOURLY_ICON_9_Y1-1)

HOURLY_HUMIDITY_7_X0 = HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_7_Y0 = HOURLY_ICON_7_Y1
HOURLY_HUMIDITY_7_X1 = HOURLY_HUMIDITY_7_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_7_Y1 = HOURLY_HUMIDITY_7_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_7_COORDS = (HOURLY_HUMIDITY_7_X0, HOURLY_HUMIDITY_7_Y0, HOURLY_HUMIDITY_7_X1, HOURLY_HUMIDITY_7_Y1)

HOURLY_HUMIDITY_8_X0 = HOURLY_HUMIDITY_7_X1 + HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_8_Y0 = HOURLY_ICON_8_Y1
HOURLY_HUMIDITY_8_X1 = HOURLY_HUMIDITY_8_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_8_Y1 = HOURLY_HUMIDITY_8_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_8_COORDS = (HOURLY_HUMIDITY_8_X0, HOURLY_HUMIDITY_8_Y0, HOURLY_HUMIDITY_8_X1, HOURLY_HUMIDITY_8_Y1)

HOURLY_HUMIDITY_9_X0 = HOURLY_HUMIDITY_8_X1 + HOURLY_HUMIDITY_GAP
HOURLY_HUMIDITY_9_Y0 = HOURLY_ICON_9_Y1
HOURLY_HUMIDITY_9_X1 = HOURLY_HUMIDITY_9_X0 + HOURLY_HUMIDITY_BOX_SIZE[0]
HOURLY_HUMIDITY_9_Y1 = HOURLY_HUMIDITY_9_Y0 + HOURLY_HUMIDITY_BOX_SIZE[1]
HOURLY_HUMIDITY_9_COORDS = (HOURLY_HUMIDITY_9_X0, HOURLY_HUMIDITY_9_Y0, HOURLY_HUMIDITY_9_X1, HOURLY_HUMIDITY_9_Y1)

# Lists with coordinates on the TFT
time_coords = [HOURLY_TIME_1_COORDS, HOURLY_TIME_2_COORDS, HOURLY_TIME_3_COORDS, HOURLY_TIME_4_COORDS, HOURLY_TIME_5_COORDS, HOURLY_TIME_6_COORDS, HOURLY_TIME_7_COORDS, HOURLY_TIME_8_COORDS, HOURLY_TIME_9_COORDS]
temp_coords = [HOURLY_TEMP_1_COORDS, HOURLY_TEMP_2_COORDS, HOURLY_TEMP_3_COORDS, HOURLY_TEMP_4_COORDS, HOURLY_TEMP_5_COORDS, HOURLY_TEMP_6_COORDS, HOURLY_TEMP_7_COORDS, HOURLY_TEMP_8_COORDS, HOURLY_TEMP_9_COORDS]
humidity_coords = [HOURLY_HUMIDITY_1_COORDS, HOURLY_HUMIDITY_2_COORDS, HOURLY_HUMIDITY_3_COORDS, HOURLY_HUMIDITY_4_COORDS, HOURLY_HUMIDITY_5_COORDS, HOURLY_HUMIDITY_6_COORDS, HOURLY_HUMIDITY_7_COORDS, HOURLY_HUMIDITY_8_COORDS, HOURLY_HUMIDITY_9_COORDS]
icon_coords = [ICON_1_COORDS, ICON_2_COORDS, ICON_3_COORDS, ICON_4_COORDS, ICON_5_COORDS, ICON_6_COORDS, ICON_7_COORDS, ICON_8_COORDS, ICON_9_COORDS]

# Colors
pink = (255, 102, 255)
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)
light_blue = (191, 253, 255)

class HourlyForecastDisplay(Display):

    def __init__(self, lat=54.9981, lon=-7.3093) -> None:
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

    def _print_forecast(self, TFT, force=False):
        # Update hourly forecast screen every 2 minutes
        # The 'force' flag bypasses the time check
        now = datetime.now()

        if (now.second == 0 and now.minute % 2 == 0) or force is True:
            try:
                # Compare time with weather object timestamp and only update if weather object is more than 120 seconds old
                weather_timestamp = datetime.utcfromtimestamp(self.weather["current"]["dt"])
                tdiff = now - weather_timestamp
                if tdiff.seconds >= 120:
                    self.weather = get_weather_data(self.lat, self.lon)
                if self.weather is not None:
                    TFT.clear()
                    self._print_hourly_forecast_v2(TFT, self.weather)
            except Exception as ex:
                print(ex)

    def _print_hourly_forecast(self, TFT, weather):
        try:
            # Get hourly forecast
            hourly_data = []
            hourly_forecast = weather["hourly"]
            hourly_forecast_len = len(hourly_forecast)

             # Need forecast for 9 hours. Normally the API responds with a 48-hours forecast.
            if (hourly_forecast_len >= 10):
             # Create strings with the values and populate a list
                for i in range(1, 10):
                    time = datetime.utcfromtimestamp(hourly_forecast[i]["dt"]).strftime("%H:%M")
                    temp = f"{hourly_forecast[i]['temp']:>4.1f}\u00b0C"
                    humidity = f"{hourly_forecast[i]['humidity']:4.1f}%"
                    icon_id = hourly_forecast[i]["weather"][0]["icon"]

                    hourly_data.append({"time": time, "temp": temp, "humidity": humidity, "icon_id": icon_id})
                    
                # Iterate over the list and print values on the LCD
                for i in range(0, 9):
                    self._tft_print_blocktext(TFT, hourly_data[i]["time"], fnt_small, HOURLY_TIME_BOX_SIZE, time_coords[i])
                    self._tft_print_blocktext(TFT, hourly_data[i]["temp"], fnt_small, HOURLY_TEMP_BOX_SIZE, temp_coords[i])
                    self._tft_print_blocktext(TFT, hourly_data[i]["humidity"], fnt_small, HOURLY_HUMIDITY_BOX_SIZE, humidity_coords[i])

                    with Image.open(Path(__file__).resolve().parents[1].joinpath("resources/SmallIcons/" + hourly_data[i]["icon_id"] + ".bmp")) as icon:
                        TFT.display_block(icon, (*icon_coords[i]))

        except Exception as ex:
            print("An exception ocurred while parsing/displaying weather", ex)

    def _print_hourly_forecast_v2(self, TFT, weather):
        try:
            # Get hourly forecast
            hourly_data = []
            hourly_forecast = weather["hourly"]
            hourly_forecast_len = len(hourly_forecast)

             # Need forecast for 6 hours. Normally the API responds with a 48-hours forecast.
            if (hourly_forecast_len >= 13):
             # Create strings with the values and populate a list
                for i in range(4, 11):
                    time = datetime.utcfromtimestamp(hourly_forecast[i]["dt"]).strftime("%H:%M")
                    temp = f"{hourly_forecast[i]['temp']:>4.1f}\u00b0C"
                    humidity = f"{hourly_forecast[i]['humidity']:4.1f}%"
                    condition = hourly_forecast[i]["weather"][0]["main"]
                    icon_id = hourly_forecast[i]["weather"][0]["icon"]

                    hourly_data.append({"time": time, "temp": temp, "humidity": humidity, "condition": condition, "icon_id": icon_id})
                    
                # Iterate over the list and print values on the LCD
                for i in range(0, 6):
                    # Create a black box, get its draw object
                    background = Image.new('RGB', (ILI9341_TFTWIDTH - ICON_WIDTH, ICON_HEIGHT), black)
                    draw = ImageDraw.Draw(background)

                    time_string_width, time_string_height = draw.textsize(hourly_data[i]["time"], fnt_large)
                    temp_string_width, temp_string_height = draw.textsize(hourly_data[i]["temp"], fnt_large)
                    humidity_string_width, humidity_string_height = draw.textsize(hourly_data[i]["humidity"], fnt_large)
                    condition_string_width, condition_string_height = draw.textsize(hourly_data[i]["condition"], fnt_large)

                    draw.text((10, 10), hourly_data[i]["time"], color=black, font=fnt_large)
                    draw.text((10, ICON_HEIGHT-condition_string_height-10), hourly_data[i]["condition"], color=black, font=fnt_large)
                    draw.text(( ILI9341_TFTWIDTH - ICON_WIDTH - temp_string_width, 10 ), hourly_data[i]["temp"], font=fnt_large )
                    draw.text(( ILI9341_TFTWIDTH - ICON_WIDTH - humidity_string_width, ICON_HEIGHT - humidity_string_height -10 ), hourly_data[i]["humidity"], font=fnt_large, fill=light_blue )

                    TFT.display_block(background, 50, 50*i, ILI9341_TFTWIDTH-1, 50*(i+1)-1)

                    with Image.open(Path(__file__).resolve().parents[1].joinpath("resources/SmallIcons/" + hourly_data[i]["icon_id"] + ".bmp")) as icon:
                        TFT.display_block(icon, 0, 50*i, 50-1, 50*(i+1)-1)

        except Exception as ex:
            print("An exception ocurred while parsing/displaying weather", ex)

    def draw(self, TFT):
        now = mktime(datetime.now().timetuple())

        # If two seconds have passed since the last time the function was called, assume
        # another display has been drawn
        if (now - self.time > 2) or not self._has_drawn_display:
            self.time = now
            self._print_forecast(TFT, force=True)
            self._has_drawn_display = True
        else:
            self.time = now
            self._print_forecast(TFT, force=False)
