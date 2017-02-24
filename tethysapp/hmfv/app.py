from tethys_sdk.base import TethysAppBase, url_map_maker


class HimalayaFloodMapVisualizer(TethysAppBase):
    """
    Tethys app class for Himalaya Flood Map Visualizer.
    """

    name = 'Himalaya Flood Map Visualizer'
    index = 'hmfv:home'
    icon = 'hmfv/images/icon.gif'
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
        )

        return url_maps