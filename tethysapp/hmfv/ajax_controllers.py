from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import os
import datetime
import  csv
import json, ast
from utilities import *
import StringIO

from .app import HimalayaFloodMapVisualizer as app
from model import Watershed
from sqlalchemy.orm.exc import ObjectDeletedError
from sqlalchemy import update

@user_passes_test(user_permission_test)
def watershed_add(request):
    """
    AJAX Controller for adding the watershed
    """
    response = {}
    if request.is_ajax() and request.method == 'POST':

        info =  request.POST

        #Parameters that will be added to the database
        display_name = info.get('display_name')
        service_folder = info.get('service_folder')
        spt_watershed = info.get('spt_watershed')
        spt_basin = info.get('spt_basin')
        spt_reach = info.get('spt_reach')
        rc_files = request.FILES.getlist('rating_curve')

        #Parsing the rating curve csv file
        for file in rc_files:
            data = StringIO.StringIO(file.read())
            firstline = True
            rc_list = []
            for row in data:
                if '\r' in row:
                    datacsvmac = row.split('\r')
                    for row1 in datacsvmac:
                        rc_json = {} #Initialize an empty json dictionary. This allows you store the values as one big json dictionary.
                        if firstline:
                           firstline = False
                           #header = row.split(",")
                           if ('Flow,Depth') not in row1: #Change this code if you want to change how strict you would like to be with the headers
                               error = "Please check the headers in the csv file."

                               response = {"error":error}
                               break
                           continue
                        features = row1.split(",")
                        #Converting the csv fields to float
                        flow = float(features[0])
                        depth = float(features[1])
                        rc_json["f"] = flow
                        rc_json["d"] = depth
                        rc_list.append(rc_json)

                else:
                    rc_json = {} #Initialize an empty json dictionary. This allows you store the values as one big json dictionary.
                    if firstline:
                       firstline = False
                       #header = row.split(",")
                       if ('Flow,Depth') not in row: #Change this code if you want to change how strict you would like to be with the headers
                           error = "Please check the headers in the csv file."

                           response = {"error":error}
                           break
                       continue
                    features = row.split(",")
                    #Converting the csv fields to float
                    flow = float(features[0])
                    depth = float(features[1])
                    rc_json["f"] = flow
                    rc_json["d"] = depth
                    rc_list.append(rc_json)

            response = {"data":rc_list,"success":"Success"}

        session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = session_maker()

        #Adding the parameters to the database
        watershed = Watershed(display_name=display_name,service_folder=service_folder,spt_watershed=spt_watershed,spt_basin=spt_basin,spt_reach=spt_reach,rc_json=str(rc_list))

        session.add(watershed)
        session.commit()
        session.close() #Always remember to close the database

    return JsonResponse(response)


@user_passes_test(user_permission_test)
def watershed_delete(request):
    """
    Controller for deleting a watershed.
    """
    if request.is_ajax() and request.method == 'POST':
        # get/check information from AJAX request
        info = request.POST
        watershed_id = info.get('watershed_id')

        if watershed_id:
            # initialize session
            # session = SessionMaker()

            session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
            session = session_maker()

            session.query(Watershed).filter(Watershed.id == watershed_id).delete(synchronize_session='evaluate') #Delete the record from the database and refresh it
            session.commit()
            session.close()

            return JsonResponse({'success': "Watershed sucessfully deleted!"})
        return JsonResponse({'error': "Cannot delete this watershed."})
    return JsonResponse({'error': "A problem with your request exists."})

@user_passes_test(user_permission_test)
def watershed_update(request):
    """
    Controller for updating a watershed.
    """

    response = {}

    #Get the recently updated data via ajax post
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        #Defining Parameters from the AJAX post request
        watershed_id = info.get('watershed_id')
        display_name = info.get('display_name')
        service_folder = info.get('service_folder')
        spt_watershed = info.get('spt_watershed')
        spt_basin = info.get('spt_basin')
        spt_reach = info.get('spt_reach')
        rc_files = request.FILES.getlist('rating_curve')

        # initialize session
        # session = SessionMaker()

        session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = session_maker()

        watershed = session.query(Watershed).get(watershed_id) #Find the relevant watershed based on the watershed id

        if rc_files: #If they re-uploaded the rating curve follow the same workflow as before to generate a json dictionary with the rating curve values

            for file in rc_files:
                data = StringIO.StringIO(file.read())
                firstline = True
                rc_list = []
                for row in data:
                    rc_json = {}
                    if firstline:
                        firstline = False
                        # header = row.split(",")
                        if ('Flow,Depth') not in row:
                            error = "Please check the headers in the csv file."
                            response = {"error": error}
                            break
                        continue
                    features = row.split(",")
                    flow = float(features[0])
                    depth = float(features[1])
                    rc_json["f"] = flow
                    rc_json["d"] = depth
                    rc_list.append(rc_json)

            #Updating the database with the newly defined parameters when a rating curve is involved
            watershed.rc_json = str(rc_list)
            watershed.display_name = display_name
            watershed.service_folder = service_folder
            watershed.spt_watershed = spt_watershed
            watershed.spt_basin = spt_basin
            watershed.spt_reach = spt_reach
            session.commit()
            session.close()
            response = {'success':'success'}

        else:
            #Updating the database with no rating curve
            watershed.display_name = display_name
            watershed.service_folder = service_folder
            watershed.spt_watershed = spt_watershed
            watershed.spt_basin = spt_basin
            watershed.spt_reach = spt_reach
            session.commit()
            session.close()
            response = {'success': 'success'}

    return JsonResponse(response)


def forecast(request):
    """
    Controller for retrieving the forecast from the streamflow prediction tool
    """

    response = {}

    if request.is_ajax() and request.method == 'POST':
        info = request.POST
        #Parameters that are needed to make a request using the streamflow prediction api
        watershed_id = info.get('watershed_id')
        forecast_date = info.get('forecast_date')
        forecast_stat = info.get('forecast_stat')

        #Connect to the database
        # session = SessionMaker()

        session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = session_maker()
        watershed = session.query(Watershed).get(watershed_id) #Get the relevant watershed based on the watershed id

        #Retrieve additional metadata from the database
        spt_watershed = watershed.spt_watershed
        spt_basin = watershed.spt_basin
        spt_reach = watershed.spt_reach
        rating_curve = ast.literal_eval(watershed.rc_json)



        forecast_url = 'https://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder={3}&stat_type={4}'.format(
                     spt_watershed, spt_basin, spt_reach,forecast_date,forecast_stat) #Streamflow Prediction Tool API request

        ts_list = get_wml_values(forecast_url) #Generate a time series from the url. See utilities.py

        ranges = []
        #Generating a list of ranges from the rating curve
        #The following snippet returns the flow values and their corresponding depth. For Example: [(0,1000,5)]. In the example 0(cfs) is the lower bound, 1000(cfs) is the upper bound, \
        # 5(m) is the depth for those streamflow ranges.
        for flow in rating_curve:
            if rating_curve.index(flow) != len(rating_curve) -1:
                next_flow = rating_curve[rating_curve.index(flow)+1]
                ranges.append((flow['f'],next_flow['f'],flow['d']))
            else:
                ranges.append((flow['f'],float(flow['f'])+1000000000, flow['d'])) #Somewhat of a hack to make the upper bound of the last one ridiculously high. This makes it easier to calculate the relevant depth.


        map_forecast = []

        #Redefining the forecast based on the rating curve values
        for date,flow in ts_list:
            for f in ranges:
                if f[0] <= flow < f[1]: #Checking if the flow falls within a given range of flows
                    flow = f[2] #If it does, then assign it the value of the corresponding depth
                    map_forecast.append([date,flow]) #A list of the forecast dates with their corresponsing depths

        response = {'success': 'success',"data":ts_list,"title":spt_watershed,"unit":"cms","map_forecast":map_forecast}
        return JsonResponse(response)









