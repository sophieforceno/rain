# rain
Rain: A self-hosted weather forecast app written in Python

Rain has several components: the Rain python module that can be run from the command-line. Provides current conditions and daily forecast for the next 5 days. Rain requires Python and the standard library only. Works with Python 3.

The second component is the rainserver component which depends on flask, flask-cache, flask-assets, flask-compress, and Cherrypy. This allows you to host your own weather forecast app on the web! The server component calls the rain module when needed to update the current conditions and forecast on the web app/server.

The commandline component, rain.py, is now available! The server componenent is very much still work in progress (it works, but let's just say... I'm not normally a web developer).

UPDATE: Not that anyone is using this other than me, but since Dark Sky has been sold to Apple, the API will no longer be available as of 2021. Get it while you can, I suppose. Given that, whatever you read above about me releasing a web-based weather app, it ain't happening :-(

### Installation
- `git clone https://github.com/andyforceno/rain.git`
- You must obtain API keys for the Dark Sky API and Google Maps API. 
  To register for Dark Sky: https://darksky.net/dev/register
  To register for Google Maps API: https://developers.google.com/maps/documentation/geolocation/get-api-key
  Note: Enable the Google Maps Geolocation API and Google Maps Geocoding API
- Insert your API keys in rain.conf, along with your residental address, save the file
- Execute `python3 rain.py -c` to see the magic happen (and see current weather conditions)
- `rain.py -h` will display help

### Usage
usage: rain [-h] [-c] [-d [{0,1,2,3,4} [{0,1,2,3,4} ...]]] [-o] [-m] [-w]

    optional arguments:
      -h, --help            show this help message and exit
  
      -c, --currently       Display currrent weather conditions
  
      -d [{0,1,2,3,4} [{0,1,2,3,4} ...]], --day [{0,1,2,3,4} [{0,1,2,3,4} ...]]
                        Display weather forecast for one or more days (0-4).
                        Days are space-delimited (e.g. rain -d 0 1 2 gives the forecast for today and the next 2 days)
                        
      -o, --hourly          Display hour-by-hour weather conditions
  
      -m, --minutely        Display minute-by-minute forecast for the next hour
  
      -w, --weekly          Display 5-day weather forecast (same as 'rain -d 0 1 2
                            3 4')

### Project Goals
- To provide a self-hosted weather forecast app that can run on myriad hardware from desktop PCs and servers to single-board computers (rain is being partly developed on a 580Mhz Onion Omega2 SBC).
- To provide a self-hosted web app that is  easy to setup, configure, and use
- To provide a self-hosted web app that is stable and provides accurate forecasts
- And more!
