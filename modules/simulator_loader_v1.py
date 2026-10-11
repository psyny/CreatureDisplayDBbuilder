import glob

from libs.serializers.jsonfile_to_obj import jsonfile_to_obj
from modules.parsing_creature_data import add_creature_data_to_db
from modules.name_filter import is_banned_name

# HeadCrawler's npc id -> name db: { "<npcid>": "<name>", "" or null }
# null means the id doesn't exist on Wowhead, "" that it exists without a name: both are skipped.
# Dev names ([UNUSED], [DNT], ...) are skipped too, see name_filter.
dbloc_template = 'dbs/{flavor}/simulator/'


def simulator_loader_v1(flavor, filename = None):
    dbloc = dbloc_template.format(flavor=flavor)

    json_files = []
    if filename != None:
        json_files.append(dbloc + filename)
    else:
        json_files = sorted(glob.glob(dbloc + '*.json'))

    dbs = []

    for json_file in json_files:
        print("Loading: " + json_file)
        sim_raw_objs = jsonfile_to_obj(json_file)
        if sim_raw_objs:
            db = {
                "ids": simulator_parser(sim_raw_objs),
                "source": "simulator_v1",
                "file": json_file,
            }

            dbs.append(db)

    return dbs


def simulator_parser(sim_raw_objs):
    ids = {}

    for nid, name in sim_raw_objs.items():
        if not name or is_banned_name(name):
            continue

        add_creature_data_to_db(ids, name, 0, [[int(nid)],[],[],], [[],[],[],])

    return ids
