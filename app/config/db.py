from sqlalchemy import create_engine, MetaData

import databases


engine = create_engine("mysql+pymysql://admin2:Rafael1510!@localhost:3306/julia2")


meta = MetaData()

conn = engine.connect()

# db = databases.Database('postgresql+asyncpg://postgres:@localhost:3306/francelina')
