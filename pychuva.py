import urllib2
from xml.dom import minidom
from urllib import urlencode
import re

GOOGLE_WEATHER_URL   = 'http://www.google.com/ig/api?%s'

def get_data(params):
    url = GOOGLE_WEATHER_URL % urlencode(params)
    handler = urllib2.urlopen(url)
    content_type = handler.info().dict['content-type']
    charset = re.search('charset\=(.*)',content_type).group(1)
    if not charset:
        charset = 'utf-8'
    if charset.lower() != 'utf-8':
        xml_response = handler.read().decode(charset).encode('utf-8')
    else:
        xml_response = handler.read()
    dom = minidom.parseString(xml_response)    
    handler.close()
    return dom

def parse_data(dom):
    weather_data = {}
    weather_dom = dom.getElementsByTagName('weather')[0]

    data_structure = { 
        'forecast_information': ('city', 'postal_code', 'latitude_e6', 'longitude_e6', 'forecast_date', 'current_date_time', 'unit_system'),
        'current_conditions': ('condition','temp_f', 'temp_c', 'humidity', 'wind_condition', 'icon')
    }           
    for (tag, list_of_tags2) in data_structure.iteritems():
        tmp_conditions = {}
        for tag2 in list_of_tags2:
            try: 
                tmp_conditions[tag2] =  weather_dom.getElementsByTagName(tag)[0].getElementsByTagName(tag2)[0].getAttribute('data')
            except IndexError:
                pass
        weather_data[tag] = tmp_conditions

    forecast_conditions = ('day_of_week', 'low', 'high', 'icon', 'condition')
    forecasts = []

    for forecast in dom.getElementsByTagName('forecast_conditions'):
        tmp_forecast = {}
        for tag in forecast_conditions:
            tmp_forecast[tag] = forecast.getElementsByTagName(tag)[0].getAttribute('data')
        forecasts.append(tmp_forecast)

    weather_data['forecasts'] = forecasts
    dom.unlink()
    return weather_data

def get_google_forecast(location, hl=""):
    params = {'weather': location, 'hl': hl}
    raw_data = get_data(params)
    return parse_data(raw_data)