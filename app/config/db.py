from sqlalchemy import create_engine, MetaData

import databases

<<<<<<< HEAD
engine = create_engine("mysql+pymysql://francelina-user:@localhost:3306/francelina")
=======
engine = create_engine("mysql+pymysql://root:@localhost:3306/francelina")
>>>>>>> 4a8c42d3c00f99defb37de7ca67f6100efe2ccb4

meta = MetaData()

conn = engine.connect()

# db = databases.Database('postgresql+asyncpg://postgres:@localhost:3306/francelina')
