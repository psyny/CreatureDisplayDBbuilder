import json
import os
import sys

from modules.wago_loader_v1 import wago_loader_v1
from modules.simulator_loader_v1 import simulator_loader_v1
from modules.idcollector_loader_v1 import idcollector_loader_v1
from modules.idcollector_loader_v2 import idcollector_loader_v2
from modules.idcollector_loader_v3 import idcollector_loader_v3
from modules.uimap_loader_v1 import uimap_loader_v1, create_zone_resolver, create_zone_ancestors, export_uimap_csv
from modules.parsing_creature_data import db_aggregator
from modules.creature_display_db import export_luafile

# Game flavors. Sources are read from dbs/<flavor>/ and written to output/CreatureDisplayDB_<flavor>_db_general.lua
# and output/<flavor>_map_map.csv
FLAVORS = ["retail", "forever"]

# Which sources go into the DB. The user DB is the CreatureIdCollector data.
APP_CONFIG_PATH = "app_config.json"
APP_CONFIG_DEFAULTS = {
    "add_user_db": False,
    "add_wago_db": True,
    "add_simulator_db": True,
}

def load_app_config():
    config = dict(APP_CONFIG_DEFAULTS)
    if os.path.exists(APP_CONFIG_PATH):
        with open(APP_CONFIG_PATH, encoding="utf-8") as f:
            config.update(json.load(f))
    return config

def build(flavor, config):
    print("[Building " + flavor + "]")

    # DB store
    dbs = []

    # Parse Wago DBs
    if config["add_wago_db"]:
        print("Loading Wago Databases")
        tdbs = wago_loader_v1(flavor)
        dbs.extend(tdbs)

    # Parse Simulator DBs (HeadCrawler npc id -> name), ranked right after Wago
    if config["add_simulator_db"]:
        print("Loading Simulator Databases")
        tdbs = simulator_loader_v1(flavor)
        dbs.extend(tdbs)

    if config["add_user_db"]:
        # Parse Id Collector V1 DBs
        print("Loading Id Collector V1 Databases")
        tdbs = idcollector_loader_v1(flavor)
        dbs.extend(tdbs)

        # Parse Id Collector V2 DBs
        print("Loading Id Collector V2 Databases")
        tdbs = idcollector_loader_v2(flavor)
        dbs.extend(tdbs)

        # Parse Id Collector V3 DBs (with game versions)
        print("Loading Id Collector V3 Databases")
        tdbs = idcollector_loader_v3(flavor)
        dbs.extend(tdbs)

    # Zones: zones, dungeons, micro maps, etc. are stored under their continent (see uimap_loader_v1)
    print("Loading UiMap")
    uimap = uimap_loader_v1(flavor)
    zone_resolver = create_zone_resolver(uimap)

    # Aggregate into a single DB
    print("Aggregating into a single DB")
    raw_db = db_aggregator(dbs, zone_resolver)

    # Create Lua File
    export_luafile(raw_db, "output/CreatureDisplayDB_" + flavor + "_db_general.lua", create_zone_ancestors(uimap))

    # World maps used by this flavor
    export_uimap_csv(flavor, "output/" + flavor + "_map_map.csv")


# Usage: python app.py [flavor ...]   (no flavor builds all of them)
flavors = sys.argv[1:] or FLAVORS
for flavor in flavors:
    if flavor not in FLAVORS:
        print("Unknown flavor: " + flavor + " (valid: " + ", ".join(FLAVORS) + ")")
        sys.exit(1)

app_config = load_app_config()
print("Sources: " + ", ".join(k for k, v in app_config.items() if v))

for flavor in flavors:
    build(flavor, app_config)
