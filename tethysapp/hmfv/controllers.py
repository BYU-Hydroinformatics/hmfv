from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tethys_sdk.gizmos import (Button, MessageBox, SelectInput, TextInput, ToggleSwitch)

@login_required()
def home(request):
    """
    Controller for the app home page.
    """
    context = {}

    return render(request, 'hmfv/home.html', context)

def add_watershed(request):
    """
    Controller for the app add watershed page
    """

    watershed_name_input = TextInput(display_text='Watershed Display Name',
                                     name='watershed-name-input',
                                     placeholder='e.g.: Kathmandu Flood Map',
                                     icon_append='glyphicon glyphicon-home',
                                     )
    service_folder_input = TextInput(display_text='ArcGIS Server REST Service Directory',
                                     name='service-folder-input',
                                     placeholder='http://geoserver.byu.edu/arcgis/rest/services/Nepal_Western',
                                     icon_append='glyphicon glyphicon-link',)
    spt_watershed_input = TextInput(display_text='Streamflow Prediction Tool Watershed',
                                     name='spt-watershed-name-input',
                                     placeholder='e.g.: Nepal West',
                                     icon_append='glyphicon glyphicon-tag',)

    spt_reach_id_input = TextInput(display_text='Streamflow Prediction Tool Reachid',
                                     name='spt-reach-id-input',
                                     placeholder='e.g.: 45',
                                     icon_append='glyphicon glyphicon-tag',
                                     append='For retrieving forecasts')

    add_button = Button(display_text='Add Watershed',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-watershed',
                        attributes={'id': 'submit-add-watershed'}, )

    context = {"watershed_name_input":watershed_name_input,"service_folder_input":service_folder_input,"spt_watershed_input":spt_watershed_input,"spt_reach_id_input":spt_reach_id_input,"add_button":add_button}

    return render(request, 'hmfv/add_watershed.html', context)