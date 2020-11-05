#import libraries
import COVID19Py
import json
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.tile_providers import CARTODBPOSITRON_RETINA, get_provider
import pandas as pd
import numpy as np

#Sets up API
covid19 = COVID19Py.COVID19("http://127.0.0.1:8000", data_source="jhu")

#Returns a dict {Dates: List of bokeh-format dates, Confirmed: timeline of cases, Deaths: timeline of deaths}
def timeline(country):
    location_data = covid19.getLocationByCountryCode(str(country), timelines=True)
    return({
        'Dates': pd.to_datetime(list(location_data[0]['timelines']['confirmed']['timeline'].keys())),
        'Confirmed': list(location_data[0]['timelines']['confirmed']['timeline'].values()),
        'Deaths': list(location_data[0]['timelines']['deaths']['timeline'].values()),
        })

#Returns a dict{Deaths: list of deaths, Confirmed: list of cases, Latitude: list of latitudes, Longitude: list of longitudes}
#Data should be from covid19.getLocations()
def world_data(data):
    death_list = []
    case_list = []
    lat_list = []
    long_list = []
    for country in data:
        if country['province'] == '':
            death_list.append(country['latest']['deaths'])
            case_list.append(country['latest']['confirmed'])
            #Converts lat and long to web mercator coordinates
            long_list.append(float(country['coordinates']['longitude']) * (6378137 * np.pi/180.0))
            lat_list.append(np.log(np.tan((90 + float(country['coordinates']['latitude'])) * np.pi/360.0)) * 6378137)
    return({
        'Deaths': death_list,
        'Confirmed': case_list,
        'Latitude': lat_list,
        'Longitude': long_list
        })

#Sets up plot
output_file('covid_map.html')

#Setps up geo data
geo_data = get_provider(CARTODBPOSITRON_RETINA)
m = figure(x_axis_type = "mercator", y_axis_type = "mercator", x_range=(-2000000, 6000000), y_range=(-1000000, 7000000))
m.add_tile(geo_data)

#sets up covid19 data to display on map
raw_data = covid19.getLocations()
covid_data = world_data(raw_data)
bokeh_covid_data = ColumnDataSource(data = covid_data)

print(covid_data)

#Plots data on the map
m.circle(x = "Longitude", y = "Latitude", size = 15, color = "red", source = bokeh_covid_data)
show(m)
