import requests         # for openweathermap request
import smbus2
import bme280

port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)

api_key = "b47b119999470d6b5795aee31bcfa833"

def bme280_get_temperature():
    data = bme280.sample(bus, address, calibration_params)
    return data.temperature

def bme280_get_humidity():
    data = bme280.sample(bus, address, calibration_params)
    return data.humidity

# Blagoevgrad: 42.017, 23.100

def get_weather_data(lat=54.9981, lon=-7.3093, exclude="minutely,daily"):
    """
    Returns the json object with data from openweathermap.org.
    Excludes minutely and daily forecasts by default.
    """
    url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&units=metric&appid={}".format(lat, lon, exclude, api_key)
    
    try:
        response = requests.get(url)            # get response
        status_code = response.status_code

        if status_code == 200:  
            return response.json()
        else:
            return None
    except Exception as ex:
        print("Exception in get_weather_data: ", ex)
        return None

    
def validate_weather_data(weather):
    if weather is not None and not "cod" in weather and "current" in weather:
        return  True
    else:
        return False
        

if __name__ == "__main__": 
    data = get_weather_data()
    print(data)