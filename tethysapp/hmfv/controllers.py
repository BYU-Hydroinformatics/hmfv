from django.shortcuts import render
from django.contrib.auth.decorators import login_required,user_passes_test
from tethys_sdk.gizmos import (Button, MessageBox, SelectInput, TextInput, ToggleSwitch)
from model import  Base, SessionMaker,engine,Watershed
from utilities import user_permission_test

@login_required()
def home(request):
    """
    Controller for the app home page.
    """

    #Show available watersheds
    session = SessionMaker()
    watersheds = session.query(Watershed).all()
    watershed_list = []

    for watershed in watersheds:
        watershed_list.append(("%s (Streamflow Prediction Reach %s)" % (watershed.display_name,watershed.spt_reach),watershed.id))

    watershed_select = SelectInput(display_text='Select Watershed',
                                   name='watershed_select',
                                   options=watershed_list,
                                   multiple=False, )

    context = {'watershed_select' : watershed_select,
               'watersheds_length': len(watersheds)}

    return render(request, 'hmfv/home.html', context)

def map(request):
    if request.method == 'GET':
        info = request.GET
        watershed_id = info.get('watershed_select')
        session = SessionMaker()

        watershed = session.query(Watershed).get(watershed_id)
        watershed_name =  watershed.display_name



    context = {"watershed_name":watershed_name}
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
                                     )
    service_folder_input = TextInput(display_text='ArcGIS Server REST Service Directory',
                                     name='service-folder-input',
                                     placeholder='http://geoserver.byu.edu/arcgis/rest/services/Nepal_Western/',
                                     icon_append='glyphicon glyphicon-link',)
    spt_watershed_input = TextInput(display_text='Streamflow Prediction Tool Watershed',
                                     name='spt-watershed-name-input',
                                     placeholder='e.g.: Nepal West',
                                     icon_append='glyphicon glyphicon-tag',)
    spt_basin_input = TextInput(display_text='Streamflow Prediction Tool Subbasin',
                                    name='spt-basin-name-input',
                                    placeholder='e.g.: Kandra',
                                    icon_append='glyphicon glyphicon-tag', )

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

    context = {"watershed_name_input":watershed_name_input,
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
    session = SessionMaker()
    num_watersheds = session.query(Watershed).count()
    session.close()
    edit_modal = MessageBox(name='edit_watershed_modal',
                            title='Edit Watershed',
                            message='Loading ...',
                            dismiss_button='Nevermind',
                            affirmative_button='Save Changes',
                            affirmative_attributes='id=edit_modal_submit',
                            width=500)
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
    #initialize session
    session = SessionMaker()

    RESULTS_PER_PAGE = 5

    page = int(request.GET.get('page'))

    watersheds = session.query(Watershed).all()[(page * RESULTS_PER_PAGE):((page + 1) * RESULTS_PER_PAGE)]

    session.close()

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
        # get/check information from AJAX request
        watershed_id = info.get('watershed_id')

        # initialize session
        session = SessionMaker()

        watershed = session.query(Watershed).get(watershed_id)

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
                                                initial=False, )

        add_button = Button(display_text='Add Watershed',
                            icon='glyphicon glyphicon-plus',
                            style='success',
                            name='submit-add-watershed',
                            attributes={'id': 'submit-add-watershed'}, )

        context = {
            'watershed_name_input': watershed_name_input,
            'service_folder_input':service_folder_input,
            'spt_watershed_input':spt_watershed_input,
            'spt_basin_input': spt_basin_input,
            'spt_reach_id_input':spt_reach_id_input,
            'rc_upload_toggle_switch':rc_upload_toggle_switch,
            'add_button': add_button,
            'watershed': watershed
        }

        session.close()

        return render(request, 'hmfv/edit_watershed.html', context)

