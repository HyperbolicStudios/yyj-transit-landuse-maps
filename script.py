#standard stuff
import pandas as pd
import requests
import os
from inspect import getsourcefile
from os.path import abspath
import traceback
import time

#special packages
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import shutil
import geopandas #note: much easier to install with conda

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

def filter_stops_by_route(route):
    stop_times = pd.read_csv('data/google_transit/stop_times.csv')
    stops = pd.read_csv('data/google_transit/stops.csv')
    stop_IDs = []
    for ind in stop_times.index:
        headsign = stop_times['stop_headsign'][ind]
        if headsign[:headsign.find(" ")] == str(route):
            if stop_times['stop_id'][ind] not in stop_IDs:
                stop_IDs.append(stop_times['stop_id'][ind])
    stop_codes = []
    for id in stop_IDs:
        stop_codes.append(int(stops.loc[stops['stop_id']==id]['stop_code']))

    gdf = geopandas.read_file('data/vic_shapefile_busstops/bus_stops.shp')
    gdf  =gdf[gdf['stopid'].isin(stop_codes)]
    gdf.to_file('data/script output/route {} stops.shp'.format(route))
    return
filter_stops_by_route(7)
