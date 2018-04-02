import argparse, sys
from datetime import datetime
from shlex import split
from time import ctime

def convert_unixtime(unixtime):
    """Convert Unixtime to local 12-hour datetime"""
    # First, convert Unixtime to 24-hour time """
    twenty_four = ctime(int(unixtime)).split()[3].rpartition(':')[0]
    # Then, convert 24-hour time to 12-hour time and return it """
    return datetime.strptime(twenty_four, '%H:%M').strftime("%I:%M %p").lstrip("0")

def convert_dayofweek(unixtime):
    """
    Convert Unixtime to local day of week
    Takes unix time as input, returns an int, 0-6, corresponding to days of the week
    relative to today. Today = 0, tomorrow = 1, etc.
    """
    dayofweek = datetime.fromtimestamp(int(unixtime)).strftime('%A %B %d')
    return dayofweek

def convert_hour(hour):
    """Convert time (hour) to icon name to display appropriate clock icon"""
    clock = "wi-time-" + hour
    return clock

def convert_moonphase(moonphase):
    """ 
    Convert moon phase value to human-readable moon phase description
    moonphase is a float value 0-1
    Note: There may be a bug in the API that produces inaccurate fractional lunation numbers, off by about 0.05
    This can be see by comparing results here with a lunar calendar
    """
    if moonphase == 0:
        moon = "New moon"
    elif moonphase > 0 and moonphase < 0.25:
        moon = "Waxing crescent"
    elif moonphase == 0.25:
        moon = "First quarter moon"
    elif moonphase > 0.25 and moonphase < 0.5:
        moon = "Waxing gibbous"
    elif moonphase == 0.5:
        moon = "Full moon"
    elif moonphase > 0.5 and moonphase < 0.75:
        moon = "Waning gibbous"
    elif moonphase == 0.75:
        moon = "Last quarter moon"
    elif moonphase > 0.75:
        moon = "Waning crescent"
    return moon

def convert_wind(degrees):
    """ 
    Convert wind direction in degrees to bearing in geomagnetic coordinates
    by steve-gregory on StackOverflow: https://stackoverflow.com/a/7490772/3605584
    """
    if degrees >= 0 and degrees <= 360:obtain
        div = int((degrees/22.5)+.5)
        wind_bearing = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        return wind_bearing[(div % 16)]
    else:
        raise ValueError("Degrees out of bounds")

def get_temp_unit():
    """ 
    If unit setting in rain.conf is x then set temp unit to y. 
    Is there a way to leverage API response objects to do this instead?
    """
    # This is so the correct temperature unit is displayed in CLI output and on the web interface
    # A work in progress. For now, temperature unit will always be F even if the number is not

def pick_icon(icon):
    """Convert Dark Sky API icon data-point to weather-icons.css format"""
    icon = "wi-forecast-io-" + icon
    return icon