from .app import HimalayaFloodMapVisualizer as app
from model import Base, Watershed

def init_main_db(engine, first_time):
    Base.metadata.create_all(engine)
    if first_time:
        # session = SessionMaker()
        session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = session_maker()
        session.commit()
        session.close()