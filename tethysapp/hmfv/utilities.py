import requests,ast, urllib2
from owslib.waterml.wml11 import WaterML_1_1 as wml11
import urllib2, json
from pyproj import Proj, transform
from itertools import tee, islice, chain, izip


def user_permission_test(user):
    return user.is_superuser or user.is_staff

def get_forecast_dates(url):
    response = requests.get(url,
                         headers={'Authorization': 'Token 72b145121add58bcc5843044d9f1006d9140b84b'})
    result = ast.literal_eval(response.content)
    dates = [n.strip() for n in result]
    date_options = []
    for date in dates:
        if len(date) > 10:
            display_date = date[6:8] + '/' + date[4:6] + '/' + date[:4] + ' Noon'
        else:
            display_date = date[6:8] + '/' + date[4:6] + '/' + date[:4] + ' Midnight'
            # print display_date
        date_options.append([display_date, date])


    return date_options

def get_wml_values(url):
    response = urllib2.urlopen(urllib2.Request(url,headers={'Authorization': 'Token 72b145121add58bcc5843044d9f1006d9140b84b'}))
    data = response.read()
    series = wml11(data).response
    var = series.get_series_by_variable(var_name='Flow Forecast')
    vals = var[0].values[0]
    date_vals = vals.get_date_values()
    data = [[a, float(b)] for a, b in date_vals]

    return data

def get_layers(url):

    layers_url = url+"?f=json"
    r = requests.get(layers_url)
    # print r.json()
    json_obj = r.json()

    layers = {'list':[]}
    for service in json_obj["services"]:

        layer_list = service["name"].split("/")
        layer = layer_list[1]
        lyr_desc_url = url+'/'+layer+'/'+service['type']+'/?f=json'
        lyr_req = requests.get(lyr_desc_url)
        lyr_json_obj = lyr_req.json()
        full_extent = lyr_json_obj["fullExtent"]
        proj_id = full_extent["spatialReference"]["wkid"]
        proj_str = 'epsg:'+str(proj_id)
        in_proj = Proj(init=proj_str)
        out_proj = Proj(init='epsg:3857')
        x1,y1 = full_extent["xmin"],full_extent["ymin"]
        xmin,ymin = transform(in_proj,out_proj,x1,y1)
        x2, y2 = full_extent["xmax"], full_extent["ymax"]
        xmax,ymax = transform(in_proj,out_proj,x2,y2)
        extent = [xmin,ymin,xmax,ymax]

        metadata = lyr_json_obj["layers"]
        layer_json = {"layer":layer,"extent":extent,"metadata":metadata}
        layers['list'].append(layer_json)

    return layers

def get_time_step(layers):
    timestep = {}

    depths = []
    for layer in layers['list']:
        layer_str = layer['layer'].split('_')
        depth_str = str(layer_str[1])
        depth_str = depth_str[:1]+'.'+depth_str[1:]
        depth = float(depth_str)
        depths.append(depth)

    depths = sorted(depths)

    difference = [j-i for i,j in zip(depths[:-1],depths[1:])]
    step = sum(difference)/float(len(difference))
    max_depth = max(depths)
    timestep = {"step":step,"max_depth":max_depth}

    return timestep

def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return izip(prevs, items, nexts)