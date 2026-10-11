# Base ids come from the game's Creature table (wago). They are tracked so zone 0 can keep all of them
# and cap the ids that only come from the other sources (see creature_display_db.create_cddb).
# Simulator npc ids (HeadCrawler's npc id -> name db) are tracked the same way, ranked right after the base ids.
def add_creature_data_to_db(db, name, zoneid, nids, dids, is_base = False, is_simulator = False):
    def get_id_obj():
        obj = {
                    "nids": [set(),set(),set(),],
                    "dids": [set(),set(),set(),],
                    "base_nids": set(),
                    "base_dids": set(),
                    "simulator_nids": set(),
                }
        return obj

    # Get current creature data from DB
    creature_db = db.get(name)
    if not creature_db:
        creature_db = {
            "name": name,
            "zone": {},
        }
        creature_db["zone"][0] = get_id_obj()
        creature_db["zone"][zoneid] = get_id_obj()        
        db[name] = creature_db

    # Extend creature data from DB
    zone_data_general = creature_db["zone"].get(0)
    zone_data = creature_db["zone"].get(zoneid)
    if zone_data == None:
        zone_data = get_id_obj()
        creature_db["zone"][zoneid] = zone_data

    for i in range(3):
        for nid in nids[i]:
            if nid > 0:
                zone_data["nids"][i].add(nid)
                zone_data_general["nids"][i].add(nid)
                if is_base:
                    zone_data_general["base_nids"].add(nid)
                if is_simulator:
                    zone_data_general["simulator_nids"].add(nid)
        for did in dids[i]:
            if did > 0:
                zone_data["dids"][i].add(did)        
                zone_data_general["dids"][i].add(did)     
                if is_base:
                    zone_data_general["base_dids"].add(did)


# zone_resolver maps each recorded zone id to the zone id it's stored under (see uimap_loader_v1.create_zone_resolver)
def db_aggregator(dbs, zone_resolver = None):
    aggdb = {}

    for db in dbs:
        ids = db.get("ids")
        if not ids:
            print("DB: " + db.get("source","UNKNOWN") + " of file " + db.get("file","UNKNOWN") + " has no IDS")
            continue

        is_base = db.get("source") == "wago_v1"
        is_simulator = db.get("source") == "simulator_v1"

        for cname, cdata in ids.items():
            for zone_id, zdata in cdata.get("zone", {}).items():                
                nids = zdata["nids"]
                dids = zdata["dids"]
                if zone_resolver:
                    zone_id = zone_resolver(zone_id)
                add_creature_data_to_db(aggdb, cname, zone_id, nids, dids, is_base, is_simulator)

    return aggdb

