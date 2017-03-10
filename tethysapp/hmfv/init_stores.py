from model import engine, SessionMaker, Base, Watershed

def init_main_db(first_time):
    Base.metadata.create_all(engine)
    if first_time:
        session = SessionMaker()
        session.commit()
        session.close()