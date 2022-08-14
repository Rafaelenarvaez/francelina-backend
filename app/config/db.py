from sqlalchemy import create_engine, MetaData

engine = create_engine  ("mysql+pymysql://rafael:r15a151!@localhost:3306/admin-francelina")

meta = MetaData()

conn = engine.connect()