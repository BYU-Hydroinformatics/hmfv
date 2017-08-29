from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String
from geoalchemy2 import Geometry

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


class Communities(Base):
    """
    Communities DB model
    """

    __tablename__ = 'communities'

    # Columns
    id = Column(Integer, primary_key=True)
    watershed = Column(String)
    flood_index = Column(String)
    name = Column(String)
    point_x = Column(Float)
    point_y = Column(Float)
    geometry = Column(Geometry('POINT'))
