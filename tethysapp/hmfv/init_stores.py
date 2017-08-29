from model import Base, Communities

import os

def init_main_db(engine, first_time):

    from .app import HimalayaFloodMapVisualizer as app

    Base.metadata.create_all(engine)
    if first_time:
        session_maker = app.get_persistent_store_database('main_db', as_sessionmaker=True)
        session = session_maker()

        app_dir = os.path.dirname(__file__)
        data_path = os.path.join(app_dir, 'data')

        dir_list = os.listdir(data_path)
        for dir in dir_list:
            file_dir = os.path.join(data_path, dir)
            if os.path.isdir(file_dir):
                file_list = os.listdir(file_dir)
                for file in file_list:
                    with open(os.path.join(file_dir, file), 'r') as f:
                        lines = f.read().splitlines()
                        lines.pop(0)

                        for line in lines:
                            row = line.split(',')

                            community_row = Communities(
                                watershed=dir,
                                flood_index=file.split('.')[0],
                                name=row[2],
                                point_x=row[0],
                                point_y=row[1],
                                geometry='SRID=3857;POINT({0} {1})'.format(row[0], row[1])
                            )

                            session.add(community_row)

        session.commit()
        session.close()
