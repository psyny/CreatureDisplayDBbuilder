from modules.wago_loader_v1 import wago_loader_v1
from modules.idcollector_loader_v1 import idcollector_loader_v1
from modules.idcollector_loader_v2 import idcollector_loader_v2
from modules.parsing_creature_data import db_aggregator
from modules.creature_display_db import export_luafile

# DB store
dbs = []

# Parse Wago DBs
print("Loading Wago Databases")
tdbs = wago_loader_v1()
dbs.extend(tdbs)

# Parse Id Collector V1 DBs
print("Loading Id Collector V1 Databases")
tdbs = idcollector_loader_v1()
dbs.extend(tdbs)

# Parse Id Collector V2 DBs
print("Loading Id Collector V2 Databases")
tdbs = idcollector_loader_v2()
dbs.extend(tdbs)

# Aggregate into a single DB
print("Aggregating into a single DB")
raw_db = db_aggregator(dbs)

# Create Lua File
export_luafile(raw_db, "output/CreatureDisplayDBdb.lua")
