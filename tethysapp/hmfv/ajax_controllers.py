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
from model import Base,engine,SessionMaker,Watershed
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
        display_name = info.get('display_name')
        service_folder = info.get('service_folder')
        spt_watershed = info.get('spt_watershed')
        spt_basin = info.get('spt_basin')
        spt_reach = info.get('spt_reach')
        rc_files = request.FILES.getlist('rating_curve')

        for file in rc_files:
            data = StringIO.StringIO(file.read())
            firstline = True
            rc_list = []
            for row in data:
                rc_json = {}
                if firstline:
                   firstline = False
                   #header = row.split(",")
                   if ('Flow,Depth') not in row:
                       error = "Please check the headers in the csv file."

                       response = {"error":error}
                       break
                   continue
                features = row.split(",")
                flow = float(features[0])
                depth = float(features[1])
                rc_json["f"] = flow
                rc_json["d"] = depth
                rc_list.append(rc_json)
                response = {"data":rc_list,"success":"Success"}

        Base.metadata.create_all(engine)
        session = SessionMaker()
        watershed = Watershed(display_name=display_name,service_folder=service_folder,spt_watershed=spt_watershed,spt_basin=spt_basin,spt_reach=spt_reach,rc_json=str(rc_list))

        session.add(watershed)
        session.commit()
        session.close()

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
            session = SessionMaker()

            session.query(Watershed).filter(Watershed.id == watershed_id).delete(synchronize_session='evaluate')
            session.commit()
            session.close()

            return JsonResponse({'success': "Watershed sucessfully deleted!"})
        return JsonResponse({'error': "Cannot delete this watershed."})
    return JsonResponse({'error': "A problem with your request exists."})

@user_passes_test(user_permission_test)
def watershed_update(request):
    response = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST

        watershed_id = info.get('watershed_id')
        display_name = info.get('display_name')
        service_folder = info.get('service_folder')
        spt_watershed = info.get('spt_watershed')
        spt_basin = info.get('spt_basin')
        spt_reach = info.get('spt_reach')
        rc_files = request.FILES.getlist('rating_curve')

        # initialize session
        session = SessionMaker()

        watershed = session.query(Watershed).get(watershed_id)

        if rc_files:

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
    response = {}
    if request.is_ajax() and request.method == 'POST':
        info = request.POST
        watershed_id = info.get('watershed_id')
        forecast_date = info.get('forecast_date')
        forecast_stat = info.get('forecast_stat')

        session = SessionMaker()
        watershed = session.query(Watershed).get(watershed_id)

        spt_watershed = watershed.spt_watershed
        spt_basin = watershed.spt_basin
        spt_reach = watershed.spt_reach
        rating_curve = ast.literal_eval(watershed.rc_json)



        forecast_url = 'https://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetWaterML/?watershed_name={0}&subbasin_name={1}&reach_id={2}&start_folder={3}&stat_type={4}'.format(
                     spt_watershed, spt_basin, spt_reach,forecast_date,forecast_stat)

        ts_list = get_wml_values(forecast_url)

        ranges = []
        for flow in rating_curve:
            if rating_curve.index(flow) != len(rating_curve) -1:
                next_flow = rating_curve[rating_curve.index(flow)+1]
                ranges.append((flow['f'],next_flow['f'],flow['d']))
            else:
                ranges.append((flow['f'],float(flow['f'])+1000000000, flow['d']))


        map_forecast = []
        for date,flow in ts_list:
            for f in ranges:
                if f[0] <= flow < f[1]:
                    flow = f[2]
                    map_forecast.append([date,flow])

        response = {'success': 'success',"data":ts_list,"title":spt_watershed,"unit":"cms","map_forecast":map_forecast}
        return JsonResponse(response)









