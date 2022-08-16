#standard stuff
import requests
import warnings
import json
import os
from inspect import getsourcefile
from os.path import abspath
import traceback
import time

import pandas as pd
import numpy as np

#special packages
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import shutil

import geopandas #note: much easier to install with conda
import plotly
import plotly.express as px

warnings.filterwarnings("ignore", message="pandas.Float64Index")
warnings.filterwarnings("ignore", message="pandas.Int64Index")

#set active directory to file location
directory = abspath(getsourcefile(lambda:0))
#check if system uses forward or backslashes for writing directories
if(directory.rfind("/") != -1):
    newDirectory = directory[:(directory.rfind("/")+1)]
else:
    newDirectory = directory[:(directory.rfind("\\")+1)]
os.chdir(newDirectory)

#function updates the stop and schedule data. Run every service season
def update_static(url='http://victoria.mapstrat.com/current/google_transit.zip', extract_to='data/google_transit'):
    shutil.rmtree(extract_to)
    print('Deleted ' + extract_to)
    http_response = urlopen(url)
    zipfile = ZipFile(BytesIO(http_response.read()))
    zipfile.extractall(path=extract_to)
    os.remove(extract_to+'.zip')
    print('Downloaded files from BC Transit. Unzipped, and renaming the following files: ')
    for filename in os.listdir(extract_to):
        print(filename)
        newname = filename[:-3]+'csv'
        os.rename(extract_to +'/'+filename,extract_to+'/'+newname)
        time.sleep(.5)
    return

def list_routes(): #examines stop data, and returns a list of routes (ex. ['1', '2', '3'...]) in the system
    stop_times = pd.read_csv('data/google_transit/stop_times.csv')
    stops = pd.read_csv('data/google_transit/stops.csv')
    print("Creating list of routes...")
    routes = []
    for ind in stop_times.index:
        headsign = stop_times['stop_headsign'][ind]
        route_number = headsign[:headsign.find(" ")]
        if route_number[-1].isalpha() == True:
            route_number = route_number[:-1]
        if route_number not in routes and headsign != "Drop Off Only":
            routes.append(route_number)

    return(routes)

def filter_stops_by_route(route): #input a route. Creates a shapefile containing points  representing each stop served by the route. **Includes stops served by route variants, e.x. 7N
    stop_times = pd.read_csv('data/google_transit/stop_times.csv')
    stops = pd.read_csv('data/google_transit/stops.csv')
    print("Creating list of stops...")
    stop_IDs = []
    for ind in stop_times.index:
        headsign = stop_times['stop_headsign'][ind]
        route_number = headsign[:headsign.find(" ")]
        if route_number[-1].isalpha() == True:
            route_number = route_number[:-1]
        if route_number == route:
            if stop_times['stop_id'][ind] not in stop_IDs:
                stop_IDs.append(stop_times['stop_id'][ind])
    stop_codes = []
    for id in stop_IDs:
        stop_codes.append(int(stops.loc[stops['stop_id']==id]['stop_code']))
    print("{} stops identified. Creating stop shapefiles...".format(len(stop_codes)))

    stops = geopandas.read_file('data/vic_shapefile_busstops/bus_stops.shp')
    stops = stops[stops['stopid'].isin(stop_codes)]

    stops.to_file("data/filtered stops/route {} stops.shp".format(route))
    return

def map(routes): #Input a LIST of routes. Creates ONE html file showing the transit zoning map, for the list of routes.
    stops = geopandas.read_file("data/filtered stops/route {} stops.shp".format(routes[0]))

    if len(routes) > 0:
        for i in range(1,len(routes)):
            stops = stops.append(geopandas.read_file("data/filtered stops/route {} stops.shp".format(routes[i])))

    #Create buffer and clip zoning
    zones = geopandas.read_file('data/zoning/Harmonized_Zones_Dissolved.shp')
    buf = stops.buffer(distance = 400, resolution = 1)
    clipped_zones = geopandas.clip(zones,buf)
    clipped_zones = clipped_zones.explode()
    clipped_zones = clipped_zones.to_crs('EPSG:4326')

    clipped_zones.index = range(0,len(clipped_zones))
    data = clipped_zones

    legend = {
        "Commercial":plotly.colors.sequential.Viridis[0],
        "Apartment":plotly.colors.sequential.Viridis[2],
        "Apartment":plotly.colors.sequential.Viridis[2],
        "Comprehensive Development": plotly.colors.sequential.Viridis[6],
        "Mixed Use":plotly.colors.sequential.Viridis[4],
        "Missing Middle":plotly.colors.sequential.Viridis[8],
        "Single/Duplex":plotly.colors.sequential.Viridis[9],
        "Rural Residential":"rgb(246, 139, 69)",
        "Agricultural":"rgb(246, 139, 69)",
        "Recreational": "green",
        "Industrial": "blue",
        "Institutional": "grey",
        "Unclassified":"white"
        }

    fig = px.choropleth_mapbox(data, geojson=data.geometry, locations=data.index, color='SIMPLIFIED',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           mapbox_style="carto-positron",
                           zoom=12, center = {"lat": 48.4284, "lon": -123.3656},
                           opacity=.5,
                            color_discrete_map=legend,
                                category_orders={"SIMPLIFIED":legend.keys()}
                          )
    stops = stops.to_crs('EPSG:4326')

    fig1 = px.scatter_mapbox(stops,
                    lat=stops.geometry.y,
                    lon=stops.geometry.x,
                    hover_name="stopname",
                    mapbox_style="carto-positron",
                    zoom=12, center = {"lat": 48.4284, "lon": -123.3656}
                    )

    fig.add_trace(fig1.data[0])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #fig.show()
    title = ""
    for route in routes:
        title = title + route + " "

    fig.write_html('charts/{}.html'.format(title.strip()))
    return

def create_all_maps(): #Combine everything together
    routes = list_routes()
    print(routes)
    for route in routes:
        print("Processing route " + route)
        filter_stops_by_route(route)
        map([route])

create_all_maps()
