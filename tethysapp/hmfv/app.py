from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.stores import PersistentStore

class HimalayaFloodMapVisualizer(TethysAppBase):
    """
    Tethys app class for Himalaya Flood Map Visualizer.
    """

    name = 'Himalaya Flood Map Visualizer'
    index = 'hmfv:home'
    icon = 'hmfv/images/flood.png'
    package = 'hmfv'
    root_url = 'hmfv'
    color = '#27afc4'
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
                           controller='hmfv.controllers.home'),
                    UrlMap(name='map',
                           url='hmfv/map',
                           controller='hmfv.controllers.map'),
                    UrlMap(name='forecast',
                           url='hmfv/map/forecast',
                           controller='hmfv.ajax_controllers.forecast'),
                    UrlMap(name='add-watershed',
                           url='hmfv/add-watershed',
                           controller='hmfv.controllers.add_watershed'),
                    UrlMap(name='add-watershed-ajax',
                           url='hmfv/add-watershed/submit',
                           controller='hmfv.ajax_controllers.watershed_add'),
                    UrlMap(name='manage-watersheds',
                           url='hmfv/manage-watersheds',
                           controller='hmfv.controllers.manage_watersheds'),
                    UrlMap(name='manage-watersheds-table',
                           url='hmfv/manage-watersheds/table',
                           controller='hmfv.controllers.manage_watersheds_table'),
                    UrlMap(name='manage-watersheds-edit',
                           url='hmfv/manage-watersheds/edit',
                           controller='hmfv.controllers.edit_watershed'),
                    UrlMap(name='delete-watershed',
                           url='hmfv/manage-watersheds/delete',
                           controller='hmfv.ajax_controllers.watershed_delete'),
                    UrlMap(name='update-watershed',
                           url='hmfv/manage-watersheds/submit',
                           controller='hmfv.ajax_controllers.watershed_update'),

        )

        return url_maps

    def persistent_stores(self):
        """
        Add one or more persistent stores
        """
        stores = (PersistentStore(name='main_db',
                                  initializer='hmfv.init_stores.init_main_db',
                                  spatial=False
                                  ),
                  )

        return stores