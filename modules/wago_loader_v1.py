import glob

from libs.serializers.wagocsv_to_obj import wagocsv_to_obj
from modules.parsing_creature_data import add_creature_data_to_db
from modules.name_filter import is_banned_name

dbloc_template = 'dbs/{flavor}/wago/v1/'

def wago_loader_v1(flavor, filename = None):
    dbloc = dbloc_template.format(flavor=flavor)

    csv_files = []
    if filename != None:
        csv_files.append(dbloc + filename)
    else: 
        csv_files = sorted(glob.glob(dbloc + 'Creature.*.csv'))

    dbs = []

    for csv_file in csv_files:
        print("Loading: " + csv_file)

        ids = {}
        db = {
            "ids": ids,
            "source": "wago_v1",
            "file": csv_file,
        }
        wago_raw_objs = wagocsv_to_obj(csv_file)

        if wago_raw_objs:
            wago_objs = wago_parser(wago_raw_objs)

            for wago_obj in wago_objs.values():
                add_creature_data_to_db(ids, wago_obj["name"], 0, wago_obj["zone"][0]["nids"], wago_obj["zone"][0]["dids"])

            dbs.append(db)

    return dbs


def wago_parser(wago_raw_objs):
    ids = {}

    for wago_raw_obj in wago_raw_objs:
        if is_banned_name(wago_raw_obj["name"]):
            continue

        # wago raw obj contain only a list of non prioritized nids an dids
        add_creature_data_to_db(ids, wago_raw_obj["name"], 0, [wago_raw_obj["nids"],[],[],], [wago_raw_obj["dids"],[],[],])

    return ids