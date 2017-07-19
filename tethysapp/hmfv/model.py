from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String
# from sqlalchemy.orm import sessionmaker

# from app import HimalayaFloodMapVisualizer
#
# engine = HimalayaFloodMapVisualizer.get_persistent_store_engine('main_db')
# SessionMaker = sessionmaker(bind=engine)
Base = declarative_base()

class Watershed(Base):
    '''
    Watershed SQLAlchemy DB Model
    '''

    __tablename__ = 'watershed'

    # Table Columns

    id = Column(Integer, primary_key=True)
    display_name = Column(String)
    service_folder = Column(String)
    spt_watershed = Column(String)
    spt_basin = Column(String)
    spt_reach = Column(Integer)
    rc_json = Column(String)

    def __init__(self, display_name, service_folder, spt_watershed,spt_basin, spt_reach, rc_json):
        """
        Constructor for the table
        """
        self.display_name = display_name
        self.service_folder = service_folder
        self.spt_watershed = spt_watershed
        self.spt_basin = spt_basin
        self.spt_reach = spt_reach
        self.rc_json = rc_json