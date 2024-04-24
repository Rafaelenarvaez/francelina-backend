from sqlalchemy import create_engine, MetaData

import databases


engine = create_engine("mysql+pymysql://admin:admin1234@localhost:3306/francelina")



meta = MetaData()

conn = engine.connect()

