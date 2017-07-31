import requests,ast, urllib2
from owslib.waterml.wml11 import WaterML_1_1 as wml11
import urllib2, json
from pyproj import Proj, transform
from itertools import tee, islice, chain, izip

#Check if the user is superuser or staff. Only the superuser or staff have the permission to add and manage watersheds.
def user_permission_test(user):
    return user.is_superuser or user.is_staff

#Generate the forecast dates for a given url
def get_forecast_dates(url):
    response = requests.get(url,
                         headers={'Authorization': 'Token 72b145121add58bcc5843044d9f1006d9140b84b'}) #The token system might change in the future. Change this accordingly.
    result = ast.literal_eval(response.content)
    dates = [n.strip() for n in result]
    date_options = []
    #Creating the date options. Modifying the string so that it says Noon and Midnight.
    for date in dates:
        if len(date) > 10:
            display_date = date[6:8] + '/' + date[4:6] + '/' + date[:4] + ' Noon'
        else:
            display_date = date[6:8] + '/' + date[4:6] + '/' + date[:4] + ' Midnight'

        date_options.append([display_date, date])


    return date_options

#Get the time series for a given Streamflow Prediction tool url
def get_wml_values(url):
    response = urllib2.urlopen(urllib2.Request(url,headers={'Authorization': 'Token 72b145121add58bcc5843044d9f1006d9140b84b'}))
    data = response.read()
    series = wml11(data).response #Parsing this using the OWS Lib WML11 library
    var = series.get_series_by_variable(var_name='Flow Forecast')
    vals = var[0].values[0]
    date_vals = vals.get_date_values()
    data = [[a, float(b)] for a, b in date_vals]

    return data

#Get all the layers for given ArcGIS server service folder
def get_layers(url):
    if "arcgis" in url:
        layers_url = url+"?f=json" #Getting the results as a json object as it is easier to parse a json object
        r = requests.get(layers_url)
        json_obj = r.json()

        layers = {'list':[]}

        #Looping through each layer in the service folder
        for service in json_obj["services"]:
            layer_list = service["name"].split("/")
            layer = layer_list[1]
            lyr_desc_url = url+'/'+layer+'/'+service['type']+'/?f=json'
            lyr_req = requests.get(lyr_desc_url)
            lyr_json_obj = lyr_req.json()
            full_extent = lyr_json_obj["fullExtent"] #Get the layer extent
            proj_id = full_extent["spatialReference"]["wkid"] #Get the Layer spatial reference
            proj_str = 'epsg:'+str(proj_id)
            in_proj = Proj(init=proj_str)
            out_proj = Proj(init='epsg:3857')

            #Reprojecting the extent as a precautionary measure. This normalizes the extents if each layer is in a different projection.
            x1,y1 = full_extent["xmin"], full_extent["ymin"]
            xmin,ymin = transform(in_proj, out_proj,x1,y1)
            x2, y2 = full_extent["xmax"], full_extent["ymax"]
            xmax,ymax = transform(in_proj, out_proj, x2, y2)
            extent = [xmin, ymin, xmax, ymax]

            metadata = lyr_json_obj["layers"]
            layer_json = {"layer":layer,"extent":extent,"metadata":metadata} #Sending all the layer metadata as json object. This will make it easy to add the layer to the map.
            layers['list'].append(layer_json)

    else:
        layers_url = url + 'coveragestores.json'
        r = requests.get(layers_url)
        json_obj = r.json()

        layers = {'list':[]}

        for service in json_obj['coverageStores']['coverageStore']:
            layer = service["name"]
            lyr_desc_url = url + 'coveragestores/' + layer + '/coverages/' + layer.lower() + '.json'
            lyr_req = requests.get(lyr_desc_url)
            lyr_json_obj = lyr_req.json()
            full_extent = lyr_json_obj['coverage']['nativeBoundingBox']
            proj_str = lyr_json_obj['coverage']['srs'].lower()
            in_proj = Proj(init=proj_str)
            out_proj = Proj(init='epsg:3857')

            #Reprojecting the extent as a precautionary measure. This normalizes the extents if each layer is in a different projection.
            x1,y1 = full_extent["minx"],full_extent["miny"]
            xmin,ymin = transform(in_proj, out_proj,x1,y1)
            x2, y2 = full_extent["maxx"], full_extent["maxy"]
            xmax,ymax = transform(in_proj, out_proj, x2, y2)
            extent = [xmin, ymin, xmax, ymax]

            metadata = lyr_json_obj['coverage']['store']
            layer_json = {"layer":layer,"extent":extent,"metadata":metadata}
            layers['list'].append(layer_json)

    return layers

#Get the timesteps/depths based on the layers in the ArcGIS rest service folder
def get_time_step(layers):
    timestep = {}

    depths = []
    #Getting the layer depth as float
    for layer in layers['list']:
        layer_str = layer['layer'].split('_')
        depth_str = str(layer_str[1])
        depth_str = depth_str[:1]+'.'+depth_str[1:]
        depth = float(depth_str)
        depths.append(depth)

    depths = sorted(depths) #So that they are ordered incrementally

    difference = [j-i for i,j in zip(depths[:-1],depths[1:])] #Finding the difference in the depths
    step = sum(difference)/float(len(difference)) #Averaging the depths. Hopefully the person who created the layers created them at a constant increment.
    max_depth = max(depths)
    timestep = {"step":step,"max_depth":max_depth} #Returning the max depth and the time step. These parameters will govern the slider steps and the max value in the front end.\

    return timestep

#Leaving this here as its a neat snippet on how to get a list of the prev,current item and next item for each item in a list
def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)