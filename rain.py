#! /usr/bin/python3
# -*- coding: utf-8 -*-
import argparse, json, urllib, http.client, os, time, string, sys
import utils
from config import ParseConfig
from datetime import datetime
from subprocess import PIPE, Popen
from shlex import split

"""
Rain - A weather application for the CLI, written in Python
    by Sophie Forceno

Distributed under an MIT license. See license.md for more info.

Dark Sky API Documentation: https://darksky.net/dev/docs

TODO: [ None of this will ever happen, API is closed in 2022 :-( ] 
- Hourly & minutely output
- Better error handling
- Handle 400 errs from Darksky:
{u'code': 400, u'error': u'The given location (or time) is invalid.'}
- Mobile push notifications with flask-pushjack
"""

class Locator(object):
    """
    Sends device MAC address or physical address to Google APIs
    All functions sans get_mac_addr return latitude and longitude as a tuple
    """
    def get_mac_addr(self):
        """Read MAC address from config or return MAC address via system call"""
        config = ParseConfig()
        conf_path = os.path.dirname(__file__)
        conf_path = os.path.join(conf_path, "rain.conf")

        if os.path.isfile(conf_path) and config.read_setting("mac"):
            mac = config.read_setting("mac")
            return mac
        else:
            # Obtain devices mac addresses via system call
            ifconfig = Popen(split("ifconfig"), stdout=PIPE)
            # grep regexp from: https://stackoverflow.com/a/245925/3605584
            grep = Popen(split("grep -o -E '([[:xdigit:]]{1,2}:){5}[[:xdigit:]]{1,2}'"), stdin=ifconfig.stdout, stdout=PIPE)
            mac = grep.communicate()[0].strip()
            config.write_setting("mac", mac)
            return mac

    def get_coordinates(self):
        """
        Read location data from file if available, otherwise
        send device's mac address or residental (home) address to Google Maps APIs
        Returns latitude and longitude as a tuple
        """
        config = ParseConfig()
        conf_path = os.path.dirname(__file__)
        conf_path = os.path.join(conf_path, "rain.conf")

        if os.path.isfile(conf_path):
            # Parse config file for coordinates
            coordinates = config.read_setting("coordinates")
            if coordinates:
                return coordinates
            else:
                try:
                    # Get mac address to send to Geolocate API
                    mac = self.get_mac_addr()
                    # If obtaining mac fails, send home address to Geocode API
                except:
                    print("Obtaining coordinates via geocoding of physical address")
                    coordinates = ', '.join(map(str, self.goog_geocode(address)))
                # Otherwise, send mac address
                else:
                    try:
                        print("Obtaining coordinates via geolocation of mac address")
                        coordinates = ', '.join(map(str, self.goog_geolocate(mac)))
                    except:
                        # If sending mac address to get coordinates fails
                        # send residental address to Geocode API
                        print("Obtaining coordinates via geocoding of physical address")
                        coordinates = ', '.join(map(str, self.goog_geocode(address)))
                # Write geocoordinates to file
                config.write_setting("coordinates", coordinates)
                print("Wrote coordinates to rain.conf")
                return coordinates
        else:
            print("rain.conf not found!")
            print("Generating rain.conf...")
            config.generate_conf()
            print("Add your Dark Sky API key to rain.conf and execute rain again")
            sys.exit(1)

    def goog_geocode(self, address):
        """
        Send residental (home) address to Google Maps Geocoding API
        Returns latitude and longitude as a tuple
        """
        config = ParseConfig()
        maps_key = config.read_setting("maps_key")

        if not maps_key:
            print("Cannot obtain coordinates from geocoding API")
            print("You must add your Google Maps API key to rain.conf")
            sys.exit(1)

        # Get address from config if running client only
        if config.read_setting("server") == "no":
            address = address.translate(string.punctuation)
            address = config.read_setting("address").replace(" ", "+")
            # When running rain-server, address will be sent to rain-server via
            # POST request and urlencoded here, when goog_geocode() is called in Flask
        elif config.read_setting("server") == "yes":
            address = address.translate(string.punctuation)
            address = address.replace(" ", "+")

        request_headers = {'Accept':'application/json', 'Accept-Encoding':'gzip', 'Content-Type':'application/json'}
        request = urllib.parse.urlencode({'address': address})
        connection = http.client.HTTPSConnection('maps.googleapis.com')
        request_path = '/maps/api/geocode/json?address=%s' % (address)
        connection.request('POST', request_path, request)
        response = connection.getresponse().read().decode()
        connection.close()

        # Handle errors in API response
        if "error" in json.loads(response):
            err_code = json.loads(response)['error']['code']
            err_msg = json.loads(response)['error']['message']
            err_reason = json.loads(response)['error']['errors'][0]['reason']
            print("Error: %s - %s (reason: %s)" % (err_code, err_msg, err_reason))
            sys.exit(1)
        else:
            try:
                lat = json.loads(response)['results'][0]['geometry']['location']['lat']
                lon = json.loads(response)['results'][0]['geometry']['location']['lng']
                return lat, lon
            except:
                print("Geocoding API could not obtain coordinates")

    def goog_geolocate(self, mac):
        """
        Send MAC address to Google Maps Geolocate API
        Returns latitude and longitude as a tuple
        """
        config = ParseConfig()
        maps_key = config.read_setting("maps_key")

        if not maps_key:
            print("Cannot obtain coordinates from geolocation API")
            print("You must add your Google Maps API key to rain.conf")
            sys.exit(1)

        request_headers = {'Accept':'application/json', 'Accept-Encoding':'gzip', 'Content-Type':'application/json'}
        request = urllib.parse.urlencode({'macAddress':'mac', 'considerIp':'true'})
        connection = http.client.HTTPSConnection('www.googleapis.com')
        request_path = '/geolocation/v1/geolocate?key=%s' % (maps_key)
        connection.request('POST', request_path, request)
        response = connection.getresponse().read().decode()
        connection.close()

        # Handle errors in API response
        if "error" in json.loads(response):
            err_code = json.loads(response)['error']['code']
            err_msg = json.loads(response)['error']['message']
            err_reason = json.loads(response)['error']['errors'][0]['reason']
            print("Error: %s - %s (reason: %s)" % (err_code, err_msg, err_reason))
            sys.exit(1)
        else:
            try:
                lat = json.loads(response)['location']['lat']
                lon = json.loads(response)['location']['lng']
                return lat, lon
            except:
                print("Geolocation API could not obtain coordinates")

class Forecast(object):
    """
    Returns forecast object via Dark Sky API
    Developer's documentation: https://darksky.net/dev/docs
    """
    def get_weather(self, coordinates, forecast):
        """
        Takes a tuple of latitude, longitude and returns
        the weather forecast in JSON format. Forecast: include a list of data-blocks.
        Values for forecast: currently, minutely, hourly, daily, alerts, flags
        """
        config = ParseConfig()
        try:
            darksky_key = config.read_setting('darksky_key')
        except:
            print("No Dark Sky API key found in rain.conf!")

        # Set unit to auto if None
        units = config.read_setting('units')
        if not units:
            units = 'auto'
        self.forecast_list = []
        self.forecast_list = ["currently", "minutely", "hourly", "daily", "alerts", "flags"]
        self.includes = []
        self.excludes = []

        if forecast is "all":
            self.includes = self.forecast_list
        elif forecast is not "all":
            # Always include weather alerts
            self.includes = ["alerts"]
            self.includes.extend(forecast)

        # Forecasts to be excluded are the items in forecast_list that are not in forecast (input by user)
        self.excludes = ",".join([item for item in self.forecast_list if item not in self.includes])
        request_headers = {'Accept':'application/json', 'Accept-Encoding':'gzip', 'Content-Type':'application/json'}
        connection = http.client.HTTPSConnection('api.darksky.net')
        request_path = '/forecast/%s/%s?units=%s&exclude=%s' % (darksky_key, coordinates, units, self.excludes)
        connection.request('GET', request_path)
        # Decode needed by Python 3 to avoid str not byte error
        response = connection.getresponse().read().decode('utf-8')
        connection.close()
        self.response = json.loads(response)

        if "error" in response:
            err_txt = self.response['error']
            err_code = self.response['code']
            print("Error: %s - %s" % (err_code,err_txt))

        return self.response

    def get_alerts(self):
        """Returns special weather advisories"""
        if 'alerts' in self.response:
            self.alert = self.response['alerts'][0]['description']
            return self.alert
        else:
            self.alert = ""

    def get_currently(self):
        """
        Get current weather condition as a dict.
        Makes accessible weather data
        already obtained via get_weather(coordinates)
        """
        self.currently = self.response['currently']
        return self.currently

    def get_minutely(self):
        """Returns today's minute-by-minute forecast as a nested dict"""
        self.includes = ["minutely"]
        self.minutely = self.response['minutely']
        return self.minutely

    def get_hourly(self):
        """Returns today's hourly forecast as a nested dict"""
        self.includes = ["hourly"]
        self.hourly = self.response['hourly']
        return self.hourly

    def get_daily(self, day):
        """Returns daily forecasts (for the next 5 days) as a dict"""
        self.daily = self.response['daily']['data'][day]
        return self.daily

    def print_currently(self):
        """Prints current weather conditions"""
        if "currently" in self.includes:
            print("\nCurrent time: %s" % utils.convert_unixtime(forecast.currently['time']))
            print("Current condition: %s" % forecast.currently['summary'])
            print("Current temperature: %s F" % round(int(forecast.currently['temperature'])))
            print("Current humidity: %s%%" % round(forecast.currently['humidity']*100))
            print("Chance of rain: %s%%" % round(forecast.currently['precipProbability']*100))
            print("Nearest storm: %s mi." % forecast.currently['nearestStormDistance'])
            print("Cloud cover: %s%%" % round((forecast.currently['cloudCover']*100)))
            print("Dewpoint: %s\N{DEGREE SIGN}" % round(forecast.currently['dewPoint']))
            print("Current pressure: %s millibars" % round(forecast.currently['pressure']))
            print("Wind speed: %s mph" % round(forecast.currently['windSpeed']))
            print("Wind gust: %s mph" % round(forecast.currently['windGust']))
            print("Wind bearing: %s" % utils.convert_wind(forecast.currently['windBearing']))
            print("Visibility: %s mi.\n" % round(forecast.currently['visibility']))
        if "minutely" in self.includes:
            print("Upcoming: %s\n" % forecast.minutely['summary'])

    def print_daily(self, day):
        """Prints forecast for the day specified by forecast.get_daily(day)"""
        print("Day: %s" % utils.convert_dayofweek(self.get_daily(day)['time']))
        print("Summary: %s" % forecast.daily['summary'])
        print("High Temp.: %s at %s" % (
            round(forecast.daily['temperatureMax']), utils.convert_unixtime(
                forecast.daily['temperatureMaxTime'])))
        print("Low Temp.: %s at %s" % (
            round(forecast.daily['temperatureMin']), utils.convert_unixtime(
                forecast.daily['temperatureMinTime'])))
        print("Humidity: %s%%" % (round(forecast.daily['humidity']*100)))
        print("Chance of rain: %s%%" % (round(forecast.daily['precipProbability']*100)))
        print("Dewpoint: %s\N{DEGREE SIGN}" % round(forecast.daily['dewPoint']))
        print("Pressure: %s millibars" % round(forecast.daily['pressure']))
        print("Wind speed: %s mph" % round(forecast.daily['windSpeed']))
        print("Sunrise: %s" % utils.convert_unixtime(forecast.daily['sunriseTime']))
        print("Sunset: %s" % utils.convert_unixtime(forecast.daily['sunsetTime']))
        print("Moon Phase: %s\n" % utils.convert_moonphase(forecast.daily['moonPhase']))

    def print_alert(self):
        """Prints weather alerts, if available"""
        if forecast.alert:
            print("Special weather advisory: %s %s" % (
                utils.convert_unixtime(forecast.response['alerts'][0]['time']), forecast.alert))
            print("Severity: %s" % forecast.response['alerts'][0]['severity'])
            print("Regions: %s" % ", ".join(forecast.response['alerts'][0]['regions']))
            print("Expires: %s\n" % utils.convert_unixtime(forecast.response['alerts'][0]['expires']))

# Main
if __name__ == '__main__':
    forecast = Forecast()
    locate = Locator()
    coordinates = locate.get_coordinates()
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--currently", help="Display currrent weather conditions",
                            action="store_true")
    parser.add_argument("-d", "--day", help="Display weather forecast for one or more days (0-4). Days are space-delimited",
                            action="store", nargs='*', choices=['0','1','2','3','4'])
    parser.add_argument("-o", "--hourly", help="Display hour-by-hour weather conditions",
                            action="store_true")
    parser.add_argument("-m", "--minutely", help="Display minute-by-minute forecast for the next hour",
                                action="store_true")
    parser.add_argument("-w", "--weekly", help="Display 5-day weather forecast (same as 'rain -d 0 1 2 3 4')",
                                action="store_true")
    args = parser.parse_args()
    config = ParseConfig()
    # Parse rain.conf
    units = config.read_setting("units")
    server = config.read_setting("server")
    darksky_key = config.read_setting("darksky_key")

    if args.currently:
        forecast.get_weather(coordinates, ["currently"])
        forecast.get_currently()
        forecast.print_currently()
        forecast.get_alerts()
        forecast.print_alert()
    elif args.hourly:
        forecast.get_weather(coordinates, ["hourly"])
        forecast.get_hourly()
        forecast.get_alerts()
        forecast.print_alert()
    elif args.day:
        forecast.get_weather(coordinates, ["daily"])
        print('')
        # Get forecast for each day specified
        for day in args.day:
            forecast.get_daily(int(day))
            forecast.print_daily(int(day))
        forecast.get_alerts()
        forecast.print_alert()
    elif args.weekly:
        forecast.get_weather(coordinates, ["daily"])
        print('')
        for x in range(0, 6):
                forecast.get_daily(x)
                forecast.print_daily(x)
                print('-' * 25)
        forecast.get_alerts()
        forecast.print_alert()
    elif args.minutely:
        forecast.get_weather(coordinates, ["minutely"])
        forecast.get_minutely()
        forecast.get_alerts()
        forecast.print_alert()
    # Display help if -d is called with no values
    elif args.day == []:
        parser.print_help()
    # Display help if no arguments are supplied
    if len(sys.argv)==1:
        parser.print_help()
