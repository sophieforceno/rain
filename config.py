import configparser, os, sys

class ParseConfig(object):
    def read_setting(self, key):
        """Returns setting of a given key in rain.conf"""
        config = configparser.RawConfigParser(allow_no_value=True)
        # Get path of config.py to read rain.conf
        conf_path = os.path.dirname(__file__)
        conf_path = os.path.join(conf_path, "rain.conf")
        # TODO: Try/except
        with open(conf_path, "r") as conf_file:
            config.read(conf_path)
            setting = config.get("Settings", key)
            conf_file.close()
            return setting

    def write_setting(self, key, value):
        """ 
        Modify a setting in rain.conf by supplying
        key (setting), and the desired value
        """
        config = configparser.RawConfigParser(allow_no_value=True)
        conf_path = os.path.dirname(__file__)
        conf_path = os.path.join(conf_path, "rain.conf")
        config.read(conf_path)
        config.set("Settings", key, value)
        with open(conf_path, "w") as conf_file:
            config.write(conf_file)
            conf_file.close()

    def generate_conf(self):
        """Generates the default configuration file rain.conf"""
        config = configparser.RawConfigParser(allow_no_value=True)
        conf_path = os.path.dirname(__file__)
        conf_path = os.path.join(conf_path, "rain.conf")
        config.optionxform = str
        config.add_section("Settings")
        config.set("Settings", "# Your location in geocoordinates latitude and longitude")
        config.set("Settings", "# Rain will obtain these automatically by mac, IP, or residental (home) address (set below)")
        config.set("Settings", "Coordinates", "")
        config.set("Settings", "")
        config.set("Settings", "# Your Dark Sky API key. This is required!")
        config.set("Settings", "# Register here: https://darksky.net/dev/register")
        config.set("Settings", "darksky_key", "")
        config.set("Settings", "")
        config.set("Settings", "# Your Google Maps API Key.")
        config.set("Settings", "# You can get a key by going here: https://developers.google.com/maps/documentation/geolocation/get-api-key")
        config.set("Settings", "# Enable the Google Maps Geolocation API and Google Maps Geocoding API")
        config.set("Settings", "maps_key", "")
        config.set("Settings", "")
        config.set("Settings", "# Units of measurement. 'Auto' is the default.")
        config.set("Settings", "# Units: auto, ca, uk2, us, si")
        config.set("Settings", "units", "auto")
        config.set("Settings", "")
        config.set("Settings", "# Your residental (home) address. Used in case geolocation by mac or IP fails.")
        config.set("Settings", "# Enter address with no punctuation.")
        config.set("Settings", "address", "")
        config.set("Settings", "")
        config.set("Settings", "# MAC address, used for geolocation. Leave blank, Rain will cache your MAC address here")
        config.set("Settings", "mac", "")
        config.set("Settings", "")
        config.set("Settings", "# Set to 'yes' if you are using rain-server, otherwise set to 'no'.")
        config.set("Settings", "# 'yes' disables parsing of coordinates and address from this config")
        config.set("Settings", "# when Locator() is called from rain-server")
        config.set("Settings", "server", "no")

        with open(conf_path, "w") as conf_file:
            config.write(conf_file)
            conf_file.close()