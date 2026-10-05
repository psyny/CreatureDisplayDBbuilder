import glob

from libs.serializers.jsonfile_to_obj import jsonfile_to_obj
from modules.parsing_creature_data import add_creature_data_to_db

dbloc_template = 'dbs/{flavor}/creatureidcollector/v1/'

def idcollector_loader_v1(flavor, filename = None):
    dbloc = dbloc_template.format(flavor=flavor)

    # Priority table
    priority_table = {
        ("","talkinghead"): 0,
        ("","boss"): 0,
        ("","softgroup"): 2,
        ("",""): 2,
    }

    # Count json files
    json_files = []
    if filename != None:
        json_files.append(dbloc + filename)
    else: 
        json_files = sorted(glob.glob(dbloc + '*.json'))

    # Parse json files
    dbs = []

    for json_file in json_files:
        print("Loading: " + json_file)
        idcol_raw_objs = jsonfile_to_obj(json_file)
        if idcol_raw_objs:
            ids = idcollector_parser(idcol_raw_objs, priority_table)
            
            db = {
                    "ids": ids,
                    "source": "idcollector_loader_v1",
                    "file": json_file,
                }  

            dbs.append(db)          

    return dbs


def idcollector_parser(idcol_raw_objs, priority_table):
    db = {}

    for cname, cdata in idcol_raw_objs.items():
        add_to_db(db, cdata, priority_table)

    return db


def get_priority(world_type, creature_type, priority_table):
    priority = priority_table.get((world_type,creature_type))
    if priority != None:
        return priority
    
    priority = priority_table.get(("",creature_type))
    if priority != None:
        return priority    
    
    priority = priority_table.get((world_type,""))
    if priority != None:
        return priority        
    
    priority = priority_table.get(("",""))
    if priority != None:
        return priority     

    return 2   


def add_to_db_by_worldtype(db, world_type, creature_data, priority_table):
    cname = creature_data.get("name")
    if cname == None:
        return
    
    creature_data_by_worldtype = creature_data.get(world_type)
    if creature_data_by_worldtype == None:
        return    
    
    for creature_type, creature_data_by_type in creature_data_by_worldtype.items():
        # Build Priority
        priority = get_priority(world_type, creature_type, priority_table)

        for zone_id, creature_data_by_zone in creature_data_by_type.items():
            # Build Zone Id
            zone_id_int = None
            try:
                zone_id_int = int(zone_id)
            except ValueError:
                continue

            # Build Npc Ids (nids)
            nids = [[],[],[]]
            for nid_str in creature_data_by_zone.get("nids", []):
                try:
                    nid = int(nid_str)
                    nids[priority].append(nid)
                except ValueError:
                    continue

            # Build Display Ids (dids)
            dids = [[],[],[]]
            for did_str in creature_data_by_zone.get("dids", []):
                try:
                    did = int(did_str)
                    dids[priority].append(did)
                except ValueError:                    
                    continue      

            # Add to DB
            add_creature_data_to_db(db, cname, zone_id_int, nids, dids)
    return 


def add_to_db(db, creature_data, priority_table):
    add_to_db_by_worldtype(db, "instance", creature_data, priority_table)
    add_to_db_by_worldtype(db, "world", creature_data, priority_table)
