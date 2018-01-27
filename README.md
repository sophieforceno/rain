# rain
Rain: A self-hosted weather forecast app written in Python

Rain has several components: the Rain python module that can be run from the command-line. Provides current conditions and daily forecast for the next 5 days. Rain requires Python and the standard library only. Created with Python 3.4, but it also works with 2.7.6.

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
                        
The second component is the rainserver component which depends on flask, flask-cache. flask-compress, and Cherrypy. This allows you to host your own weather forecast app on the web! The server component calls the rain module when needed to update the current conditions and forecast on the web app/server.

Still working out some bugs, but the first component will be made public fairly soon. The server componenent is very much still work in progress (it works, but let's just say... I'm not normally a web developer).

Goals for this project:
- To provide a self-hosted weather forecast app that can run on myriad hardware from desktop PCs and servers to single-board computers (rain is being partly developed on a 580Mhz Onion Omega2 SBC).
- To provide a self-hosted web app that is  easy to setup, configure, and use
- To provide a self-hosted web app that is stable and provides accurate forecasts always
- And more! 
