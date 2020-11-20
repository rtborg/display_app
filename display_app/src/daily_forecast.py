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

# Size boxes
WEEKDAY_BOX_SIZE = fnt_large.getsize("Mon")
DATE_BOX_SIZE = fnt_large.getsize("31/12")

# Colors
pink = (255, 102, 255)
black = (0, 0, 0)
white = (255, 255, 255)
yellow = (255, 255, 0)
light_blue = (191, 253, 255)

class DailyForecastDisplay(Display):
    
    def __init__(self, lat=54.9981, lon=-7.3093) -> None:
        self.lat = lat
        self.lon = lon
        self.weather = get_weather_data(self.lat, self.lon, exclude="minutely,hourly")
        self.time = mktime(datetime.now().timetuple())
        self._has_drawn_display = False

    def _print_daily_forecast(self, TFT, weather):
        try:
            daily_data = []
            daily_forecast = weather["daily"]
            daily_forecast_len = len(daily_forecast)

            if (daily_forecast_len >= 7 and self.weather is not None):
                for i in range(1, 7):
                    weekday = datetime.utcfromtimestamp(daily_forecast[i]["dt"]).strftime("%a")
                    date = datetime.utcfromtimestamp(daily_forecast[i]["dt"]).strftime("%d/%m")
                    temp = f"{daily_forecast[i]['temp']['max']:.1f}/{daily_forecast[i]['temp']['min']:.1f}\u00b0C"
                    humidity = f"{daily_forecast[i]['humidity']:4.1f}%"
                    icon_id = daily_forecast[i]["weather"][0]["icon"]
                    condition = daily_forecast[i]["weather"][0]["main"]

                    daily_data.append({"weekday": weekday,"date": date, "temp": temp, "humidity": humidity, "icon_id": icon_id, "condition": condition})

                for i in range(0, 6):
                    # Create block for printing day and date, width = 10px more than date text, height same as icon
                    block_a = Image.new('RGB', (DATE_BOX_SIZE[0]+10, ICON_HEIGHT), black)
                    draw_a = ImageDraw.Draw(block_a)
                    day_string_width, day_string_height = draw_a.textsize(daily_data[i]["weekday"], fnt_large)
                    date_string_width, date_string_height = draw_a.textsize(daily_data[i]["date"], fnt_large)
                    draw_a.text(( ((block_a.size[0] - day_string_width) / 2), 10 ), daily_data[i]["weekday"], fill=white, font=fnt_large)
                    draw_a.text(( ((block_a.size[0] - date_string_width) / 2), (block_a.size[1] - date_string_height - 10) ), daily_data[i]["date"], fill=white, font=fnt_large)
                    TFT.display_block(block_a, 0, block_a.size[1]*i, block_a.size[0]-1, block_a.size[1]*(i+1)-1) 

                    # Print weather icon
                    with Image.open(Path(__file__).resolve().parents[1].joinpath("resources/SmallIcons/" + daily_data[i]["icon_id"] + ".bmp")) as icon:
                        TFT.display_block(icon, block_a.size[0], 50*i, block_a.size[0]+50-1, 50*(i+1)-1)

                    # Create block for description, temperature and humidity
                    block_b = Image.new('RGB', ( (ILI9341_TFTWIDTH - ICON_WIDTH - block_a.size[0]), ICON_HEIGHT ), black)
                    draw_b = ImageDraw.Draw(block_b)
                    condition_string_width, condition_string_height = draw_b.textsize(daily_data[i]["condition"], fnt_large)
                    temp_string_width, temp_string_height = draw_b.textsize(daily_data[i]["temp"], fnt_large)
                    humidity_string_width, humidity_string_height = draw_b.textsize(daily_data[i]["humidity"], fnt_large)

                    draw_b.text((5, 10), daily_data[i]["condition"], fill=yellow, font=fnt_large)
                    draw_b.text((5, (block_b.size[1] - temp_string_height - 10)), daily_data[i]["temp"], fill=white, font=fnt_large)
                    draw_b.text(((block_b.size[0] - humidity_string_width - 5), (block_b.size[1] - humidity_string_height - 10)), daily_data[i]["humidity"], fill=light_blue, font=fnt_large)

                    block_b_x0 = block_a.size[0] + ICON_WIDTH
                    TFT.display_block(block_b, block_b_x0, block_b.size[1]*i, block_b_x0+block_b.size[0]-1, block_b.size[1]*(i+1)-1)               
        except Exception as ex:
            print(ex)

    def _print_forecast(self, TFT, force=False):
        # Update daily forecast screen every 2 minutes
        # The 'force' flag bypasses the time check
        now = datetime.now()

        if (now.second == 0 and now.minute % 2 == 0) or force is True:
            try:
                # Compare time with weather object timestamp and only update if weather object is more than 120 seconds old
                weather_timestamp = datetime.utcfromtimestamp(self.weather["current"]["dt"])
                tdiff = now - weather_timestamp
                if tdiff.seconds >= 120:
                    self.weather = get_weather_data(self.lat, self.lon, exclude="minutely,hourly")
                if self.weather is not None:
                    TFT.clear()
                    self._print_daily_forecast(TFT, self.weather)
            except Exception as ex:
                print(ex)

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
            