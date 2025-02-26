from modules.wago_loader_v1 import wago_loader_v1
from modules.idcollector_loader_v1 import idcollector_loader_v1
from modules.idcollector_loader_v2 import idcollector_loader_v2
from modules.parsing_creature_data import db_aggregator
from modules.creature_display_db import export_luafile

# DB store
dbs = []

# Parse Wago DBs
tdbs = wago_loader_v1()
dbs.extend(tdbs)

# Parse Id Collector V1 DBs
tdbs = idcollector_loader_v1()
dbs.extend(tdbs)

# Parse Id Collector V2 DBs
tdbs = idcollector_loader_v2()
dbs.extend(tdbs)

#  Aggregate into a single DB
raw_db = db_aggregator(dbs)

# Create Lua File
export_luafile(raw_db, "output/CreatureDisplayDBdb.lua")
