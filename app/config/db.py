from sqlalchemy import create_engine, MetaData

import databases


engine = create_engine("mysql+pymysql://root@localhost:3306/francelina2")


meta = MetaData()

conn = engine.connect()

