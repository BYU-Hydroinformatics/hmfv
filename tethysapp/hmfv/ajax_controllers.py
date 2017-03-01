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
                rc_json["flow"] = flow
                rc_json["depth"] = depth
                rc_list.append(rc_json)
                response = {"data":rc_list,"success":"Success"}





    return JsonResponse(response)