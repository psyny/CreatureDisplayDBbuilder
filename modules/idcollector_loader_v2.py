import glob

from libs.serializers.lua_to_obj import lua_to_obj
from modules.idcollector_loader_v1 import add_to_db

dbloc_template = 'dbs/{flavor}/creatureidcollector/v2/'

def idcollector_loader_v2(flavor, filename = None):
    dbloc = dbloc_template.format(flavor=flavor)

    # Priority table
    priority_table = {
        ("","talkinghead"): 0,
        ("","boss"): 0,
        ("","softgroup"): 2,
        ("","follower"): 2,
        ("",""): 1,
    }

    # Count lua files
    lua_files = []
    if filename != None:
        lua_files.append(dbloc + filename)
    else: 
        lua_files = sorted(glob.glob(dbloc + '*.lua'))

    # Parse lua files
    dbs = []

    for lua_file in lua_files:
        print("Loading: " + lua_file)
        idcol_raw_objs = lua_to_obj(lua_file)
        if idcol_raw_objs:
            ids = idcollector_parser(idcol_raw_objs, priority_table)
            
            db = {
                    "ids": ids,
                    "source": "idcollector_loader_v1",
                    "file": lua_file,
                }  

            dbs.append(db)          

    return dbs


def idcollector_parser(idcol_raw_objs, priority_table):
    db = {}

    for cname, cdata in idcol_raw_objs.items():
        add_to_db(db, cdata, priority_table)

    return db