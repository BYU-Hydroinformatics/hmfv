from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.stores import PersistentStore

class HimalayaFloodMapVisualizer(TethysAppBase):
    """
    Tethys app class for Himalaya Flood Map Visualizer.
    """
    # Note: All of these parameters can be changed through the Site Admin Portal --> Tethys Apps --> Installed Apps
    name = 'Himalaya Flood Map Visualizer'
    index = 'hmfv:home'
    icon = 'hmfv/images/flood.png'
    package = 'hmfv'
    root_url = 'hmfv'
    color = '#27afc4' #Change this to change the primary color of the website
    description = 'Flood map viewer that works in conjunction with Streamflow Prediction Tool API.'
    tags = 'Flood'
    enable_feedback = False
    feedback_emails = []

        
    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (UrlMap(name='home',
                           url='hmfv',
                           controller='hmfv.controllers.home'), #Home Page controller (See controllers.py). Responsible for creating select watershed dropdown
                    UrlMap(name='map',
                           url='hmfv/map',
                           controller='hmfv.controllers.map'), #Map Page controller (See controllers.py). Responsible for showing the selected watershed on a map and generate the forecast interface.
                    UrlMap(name='forecast',
                           url='hmfv/map/forecast',
                           controller='hmfv.ajax_controllers.forecast'), #Controller responsible for generating the forecast from the Streamflow Prediction Tool. See ajax_controllers.py
                    UrlMap(name='add-watershed',
                           url='hmfv/add-watershed',
                           controller='hmfv.controllers.add_watershed'),#Add Watershed Page. Renders the add watershed page with the necessary inputs. See controllers.py
                    UrlMap(name='add-watershed-ajax',
                           url='hmfv/add-watershed/submit',
                           controller='hmfv.ajax_controllers.watershed_add'),#Add the watershed to the local database. This contrller parses the Rating Curve file and adds the watershed metadata to the database. See ajax_controllers.py
                    UrlMap(name='manage-watersheds',
                           url='hmfv/manage-watersheds',
                           controller='hmfv.controllers.manage_watersheds'),#Manage Watershed Page. Return the number of available watersheds in the local database. See controllers.py
                    UrlMap(name='manage-watersheds-table',
                           url='hmfv/manage-watersheds/table',
                           controller='hmfv.controllers.manage_watersheds_table'),#Generate a table based on the avaiable watersheds in the local database. See controllers.py
                    UrlMap(name='manage-watersheds-edit',
                           url='hmfv/manage-watersheds/edit',
                           controller='hmfv.controllers.edit_watershed'),#Edit Watershed Modal. Return the requested watershed to edit and then update it. See controllers.py
                    UrlMap(name='delete-watershed',
                           url='hmfv/manage-watersheds/delete',
                           controller='hmfv.ajax_controllers.watershed_delete'),#Delete the selected watershed from the local database. See ajax_controllers.py
                    UrlMap(name='update-watershed',
                           url='hmfv/manage-watersheds/submit',
                           controller='hmfv.ajax_controllers.watershed_update'),#Update the watershed as requested through the edit watershed page. See ajax_controllers.py

        )

        return url_maps

    #Declaring the database class
    def persistent_stores(self):
        """
        Add one or more persistent stores
        """
        stores = (PersistentStore(name='main_db', #Name of the database/persistent store
                                  initializer='hmfv.init_stores.init_main_db', #Location of the persistent store initialization function. See init_stores.py
                                  spatial=False
                                  ),
                  )

        return stores