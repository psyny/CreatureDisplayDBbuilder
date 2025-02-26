def add_creature_data_to_db(db, name, zoneid, nids, dids):
    def get_id_obj():
        obj = {
                    "nids": [set(),set(),set(),],
                    "dids": [set(),set(),set(),],
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
        for did in dids[i]:
            if did > 0:
                zone_data["dids"][i].add(did)        
                zone_data_general["dids"][i].add(did)     


def db_aggregator(dbs):
    aggdb = {}

    for db in dbs:
        ids = db.get("ids")
        if not ids:
            print("DB: " + db.get("source","UNKNOWN") + " of file " + db.get("file","UNKNOWN") + " has no IDS")
            continue

        for cname, cdata in ids.items():
            for zone_id, zdata in cdata.get("zone", {}).items():                
                nids = zdata["nids"]
                dids = zdata["dids"]              
                add_creature_data_to_db(aggdb, cname, zone_id, nids, dids)

    return aggdb

