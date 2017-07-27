from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from tethys_sdk.gizmos import (Button, MessageBox, SelectInput, TextInput, ToggleSwitch, TimeSeries)

from .app import HimalayaFloodMapVisualizer as app
from .model import Watershed
from utilities import *
import requests, ast, json
from django.http import HttpResponse, JsonResponse, Http404

@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    #Show available watersheds
    # session = SessionMaker()

    session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
    session = session_maker()

    watersheds = session.query(Watershed).all()
    watershed_list = []

    for watershed in watersheds:
        watershed_list.append(("%s (Streamflow Prediction Reach %s)" % (watershed.display_name,watershed.spt_reach),watershed.id)) #Generating the options for the dropdown

    watershed_select = SelectInput(display_text='Select Watershed',
                                   name='watershed_select',
                                   options=watershed_list,
                                   multiple=False, ) #Generating the dropdown with the available watersheds

    context = {'watershed_select' : watershed_select,
               'watersheds_length': len(watersheds)}

    return render(request, 'hmfv/home.html', context)

def map(request):
    """
    Controller for the map page
    """
    context = {}

    info = request.GET
    watershed_id = info.get('watershed_select') #Get the watershed id
    # session = SessionMaker() #Connect to the Database

    session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
    session = session_maker()

    #Retrieve all the metadata for that watershed
    watershed = session.query(Watershed).get(watershed_id)
    watershed_name =  watershed.display_name
    spt_watershed = watershed.spt_watershed
    spt_basin = watershed.spt_basin
    spt_reach = watershed.spt_reach
    service_folder = watershed.service_folder
    print(service_folder,'44444444')
    layers_json = get_layers(service_folder) #Get all the available layers in the ArcGIS server along with their relevant metadata. See utilities.py.

    ts_info = get_time_step(layers_json) #Get the timestep aka the depth difference for each layer. See utilities.py.
    timestep = ts_info["step"]
    max_depth = ts_info["max_depth"]
    layers_json = json.dumps(layers_json)
    #Get the available dates for the watershed using Streamflow Prediction tool api
    available_dates_url = 'https://tethys.byu.edu/apps/streamflow-prediction-tool/api/GetAvailableDates/?watershed_name={0}&subbasin_name={1}&reach_id={2}'.format(spt_watershed,spt_basin,spt_reach)
    forecast_dates = get_forecast_dates(available_dates_url) #Processing the url to generate dates dynamically. See utilities.py
    forecast_date_picker = SelectInput(display_text='Forecast Date Start',
                                             name='forecast_date_start',
                                             multiple=False,
                                             options=forecast_dates,
                                             initial=forecast_dates[0]) #Dropdown with the options to select a date

    #Options for the Statistic type
    stat_options = [('Mean','mean'),('High Resolution','high_res'),('Standard Deviation Range Upper','std_dev_range_upper'),('Standard Deviation Range Lower','std_dev_range_lower'),('Outer Range Upper','outer_range_upper'),('Outer Range Lower','outer_range_lower')]
    forecast_stat_type = SelectInput(display_text='Forecast Stat Type',
                                             name='forecast_stat_type',
                                             multiple=False,
                                             options=stat_options,
                                             initial=stat_options[0]) #Dropdown for selecting the statistic type

    get_forecast = Button(display_text='View Flood Forecast',
                          name='submit-get-forecast',
                          attributes={'id':'submit-get-forecast'},
                          ) #Get Forecast Button

    #Layers json stores the json information about each layer

    context = {"watershed_name": watershed_name,
               "watershed_id":watershed_id,
               "service_folder":service_folder,
               "timestep":timestep,
               "max_depth":max_depth,
               "layers_json":layers_json,
               "forecast_date_picker": forecast_date_picker,
               "forecast_stat_type": forecast_stat_type,
               "get_forecast": get_forecast}


    return render(request, 'hmfv/map.html', context)

@user_passes_test(user_permission_test)
def add_watershed(request):
    """
    Controller for the app add watershed page
    """

    watershed_name_input = TextInput(display_text='Watershed Display Name',
                                     name='watershed-name-input',
                                     placeholder='e.g.: Kathmandu Flood Map',
                                     icon_append='glyphicon glyphicon-home',
                                     ) #Input for the Watershed Display Name

    # server_toggle_switch = ToggleSwitch(display_text='Add Geospatial Server',
    #                                     name='server-toggle',
    #                                     on_label='Arcserver',
    #                                     off_label='Geoserver',
    #                                     on_style='info',
    #                                     off_style='info',
    #                                     initial=True,
    #                                     size='large')

    service_folder_input = TextInput(display_text='Server REST Service Directory',
                                     name='service-folder-input',
                                     placeholder='http://geoserver.byu.edu/arcgis/rest/services/Nepal_Western/',
                                     icon_append='glyphicon glyphicon-link',) #input for the ArcGIS rest service folder

    spt_watershed_input = TextInput(display_text='Streamflow Prediction Tool Watershed',
                                     name='spt-watershed-name-input',
                                     placeholder='e.g.: Nepal West',
                                     icon_append='glyphicon glyphicon-tag',) #Input for the streamflow prediction tool watershed name

    spt_basin_input = TextInput(display_text='Streamflow Prediction Tool Subbasin',
                                    name='spt-basin-name-input',
                                    placeholder='e.g.: Kandra',
                                    icon_append='glyphicon glyphicon-tag', ) #Input for the streamflow prediction tool basin input

    spt_reach_id_input = TextInput(display_text='Streamflow Prediction Tool Reachid',
                                     name='spt-reach-id-input',
                                     placeholder='e.g.: 45',
                                     icon_append='glyphicon glyphicon-tag',
                                     append='For retrieving forecasts') #Input for the streamflow prediction tool reach id

    #Note: Currently there are no validations to check if the Streamflow Prediction tool watershed,basin, and the reach id exist or not. Any validations will need to be done on the front end.

    add_button = Button(display_text='Add Watershed',
                        icon='glyphicon glyphicon-plus',
                        style='success',
                        name='submit-add-watershed',
                        attributes={'id': 'submit-add-watershed'}, ) #Add watershed button

    context = {"watershed_name_input":watershed_name_input,
               # 'server_toggle_switch': server_toggle_switch,
               "service_folder_input":service_folder_input,
               "spt_watershed_input":spt_watershed_input,
               "spt_basin_input":spt_basin_input,
               "spt_reach_id_input":spt_reach_id_input,
               "add_button":add_button}

    return render(request, 'hmfv/add_watershed.html', context)

@user_passes_test(user_permission_test)
def manage_watersheds(request):
    """
    Controller for the app manage watershed page
    """

    # session = SessionMaker() #Connecting to the database

    session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
    session = session_maker()
    num_watersheds = session.query(Watershed).count() #Get the number of records in the database
    session.close() #Close the database
    edit_modal = MessageBox(name='edit_watershed_modal',
                            title='Edit Watershed',
                            message='Loading ...',
                            dismiss_button='Nevermind',
                            affirmative_button='Save Changes',
                            affirmative_attributes='id=edit_modal_submit',
                            width=500) #Modal that shows up when you are editing the watershed
    context = {
        'initial_page': 0,
        'num_watersheds': num_watersheds,
        'edit_modal': edit_modal
    }

    return render(request, 'hmfv/manage_watersheds.html', context)

@user_passes_test(user_permission_test)
def manage_watersheds_table(request):
    """
       Controller for the app manage watershed page
       """
    #Initialize session
    # session = SessionMaker()

    session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
    session = session_maker()

    RESULTS_PER_PAGE = 5

    page = int(request.GET.get('page')) #Get pages there are

    watersheds = session.query(Watershed).all()[(page * RESULTS_PER_PAGE):((page + 1) * RESULTS_PER_PAGE)] #Get all the watersheds for that particular page

    session.close()

    #Buttons to navigate the pages

    prev_button = Button(display_text='Previous',
                         name='prev_button',
                         attributes={'class': 'nav_button'})

    next_button = Button(display_text='Next',
                         name='next_button',
                         attributes={'class': 'nav_button'})

    context = {'watersheds': watersheds,
                'prev_button': prev_button,
                'next_button': next_button,}
    return render(request, 'hmfv/manage_watersheds_table.html', context)


@user_passes_test(user_permission_test)
def edit_watershed(request):
    """
    Controller for the app manage_watersheds page.
    """
    if request.method == 'GET':
        info = request.GET
        # Get/Check information from AJAX request
        watershed_id = info.get('watershed_id')

        # initialize session
        # session = SessionMaker()

        session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = session_maker()

        watershed = session.query(Watershed).get(watershed_id) #Get the selected watershed

        #Same as rendering the add watershed page. Now assigning values from the database.

        watershed_name_input = TextInput(display_text='Watershed Display Name',
                                         name='watershed-name-input',
                                         placeholder='e.g.: Kathmandu Flood Map',
                                         icon_append='glyphicon glyphicon-home',
                                         initial=watershed.display_name,
                                         )

        service_folder_input = TextInput(display_text='ArcGIS Server REST Service Directory',
                                         name='service-folder-input',
                                         placeholder='http://geoserver.byu.edu/arcgis/rest/services/Nepal_Western/',
                                         icon_append='glyphicon glyphicon-link',
                                         initial=watershed.service_folder)

        spt_watershed_input = TextInput(display_text='Streamflow Prediction Tool Watershed',
                                        name='spt-watershed-name-input',
                                        placeholder='e.g.: Nepal West',
                                        icon_append='glyphicon glyphicon-tag',
                                        initial=watershed.spt_watershed)

        spt_basin_input = TextInput(display_text='Streamflow Prediction Tool Subbasin',
                                    name='spt-basin-name-input',
                                    placeholder='e.g.: Kandra',
                                    icon_append='glyphicon glyphicon-tag',
                                    initial=watershed.spt_basin)

        spt_reach_id_input = TextInput(display_text='Streamflow Prediction Tool Reachid',
                                       name='spt-reach-id-input',
                                       placeholder='e.g.: 45',
                                       icon_append='glyphicon glyphicon-tag',
                                       append='For retrieving forecasts',
                                       initial=watershed.spt_reach)

        rc_upload_toggle_switch = ToggleSwitch(display_text='Re-Upload Rating Curve?',
                                                name='rc-upload-toggle',
                                                on_label='Yes',
                                                off_label='No',
                                                on_style='success',
                                                off_style='danger',
                                                initial=False, ) #Toggle switch in case you want to re-upload the rating curve file

        add_button = Button(display_text='Add Watershed',
                            icon='glyphicon glyphicon-plus',
                            style='success',
                            name='submit-add-watershed',
                            attributes={'id': 'submit-add-watershed'}, )

        context = {
            'watershed_name_input': watershed_name_input,
            'service_folder_input': service_folder_input,
            'spt_watershed_input': spt_watershed_input,
            'spt_basin_input': spt_basin_input,
            'spt_reach_id_input': spt_reach_id_input,
            'rc_upload_toggle_switch': rc_upload_toggle_switch,
            'add_button': add_button,
            'watershed': watershed
        }

        session.close()

        return render(request, 'hmfv/edit_watershed.html', context)

