import glob

from libs.serializers.lua_to_obj import lua_to_obj
from modules.idcollector_loader_v1 import add_to_db

# CreatureIdCollector SavedVariables with game versions:
#     CreatureIdCollectorDB[name][gameVersion] = { name, world = {...}, instance = {...} }
# gameVersion is GetBuildInfo()'s version string ("12.0.1", "1.15.8", ...), or "legacy" for data saved
# before versions were tracked.
dbloc_template = 'dbs/{flavor}/creatureidcollector/v3/'

LEGACY_VERSION = "legacy"

# Retail versions are 10.0 and up, every classic client so far is below that
RETAIL_MIN_MAJOR_VERSION = 10


# Returns the flavor a game version belongs to, or None if it can't be told ("legacy" or malformed)
def flavor_of_version(game_version):
    try:
        major = int(str(game_version).split(".")[0])
    except ValueError:
        return None

    if major >= RETAIL_MIN_MAJOR_VERSION:
        return "retail"
    return "forever"


def idcollector_loader_v3(flavor, filename = None):
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
        idcol_raw_objs = lua_to_obj(lua_file, "CreatureIdCollectorDB")
        if idcol_raw_objs:
            ids = idcollector_parser(idcol_raw_objs, priority_table, flavor, lua_file)

            db = {
                    "ids": ids,
                    "source": "idcollector_loader_v3",
                    "file": lua_file,
                }

            dbs.append(db)

    return dbs


# Records of other flavors are skipped. "legacy" records have no version, so they're
# trusted to belong to the flavor of the folder they're in.
def idcollector_parser(idcol_raw_objs, priority_table, flavor, lua_file):
    db = {}
    skipped_versions = {}

    for cname, cdata_by_version in idcol_raw_objs.items():
        if not isinstance(cdata_by_version, dict):
            continue

        for game_version, cdata in cdata_by_version.items():
            if not isinstance(cdata, dict):
                continue

            version_flavor = flavor_of_version(game_version)
            if version_flavor is not None and version_flavor != flavor:
                skipped_versions[game_version] = skipped_versions.get(game_version, 0) + 1
                continue

            add_to_db(db, cdata, priority_table)

    for game_version, count in sorted(skipped_versions.items()):
        print(f"  skipped {count} records of version {game_version} (not {flavor}) in {lua_file}")

    return db
