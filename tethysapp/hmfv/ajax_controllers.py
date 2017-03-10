from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import os
import datetime
import  csv
import json
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








