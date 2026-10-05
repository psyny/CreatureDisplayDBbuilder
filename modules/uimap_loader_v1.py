import csv
import glob
import os
import re

dbloc_template = 'dbs/{flavor}/wago/v1/'

# UiMap.Type values (Enum.UIMapType)
UI_MAP_TYPE_CONTINENT = 2
UI_MAP_TYPE_ZONE = 3

# Maps deeper than this type (higher value) are stored under their nearest parent of this type
COLLAPSE_TO_TYPE = UI_MAP_TYPE_CONTINENT

# UiMap.System value for the world map. Other systems (taxi, adventure, minimap) are not used for zones.
UI_MAP_SYSTEM_WORLD = 0

MAX_CHAIN_DEPTH = 30


def _file_version(file_path):
    # UiMap.12.1.5.70077.csv -> (12, 1, 5, 70077)
    match = re.match(r'UiMap\.([\d.]+)\.csv$', os.path.basename(file_path))
    if not match:
        return ()
    return tuple(int(part) for part in match.group(1).split('.'))


# Returns the latest UiMap.<version>.csv of a flavor, or None if there's none
def _latest_uimap_file(flavor):
    dbloc = dbloc_template.format(flavor=flavor)

    csv_files = glob.glob(dbloc + 'UiMap.*.csv')
    if not csv_files:
        return None

    return max(csv_files, key=_file_version)


# Loads the latest UiMap.<version>.csv of a flavor. Returns { uiMapID: { "parent", "type", "system" } } or None if there's none.
def uimap_loader_v1(flavor):
    csv_file = _latest_uimap_file(flavor)
    if csv_file is None:
        print("No UiMap file for " + flavor + ", zone ids are kept as they are")
        return None

    print("Loading: " + csv_file)

    uimap = {}
    with open(csv_file, encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            uimap[int(row["ID"])] = {
                "parent": int(row["ParentUiMapID"]),
                "type": int(row["Type"]),
                "system": int(row["System"]),
            }

    return uimap


EXPORT_COLUMNS = ["Name_lang", "ID", "ParentUiMapID", "Type"]

# Writes the latest UiMap.<version>.csv of a flavor to file_path, keeping only world maps (System == 0)
# and the EXPORT_COLUMNS columns, in the original row order. Does nothing if the flavor has no UiMap file.
def export_uimap_csv(flavor, file_path):
    csv_file = _latest_uimap_file(flavor)
    if csv_file is None:
        print("No UiMap file for " + flavor + ", " + file_path + " not written")
        return

    print("Writing: " + file_path)
    with open(csv_file, encoding="utf-8", newline="") as source, open(file_path, "w", encoding="utf-8", newline="") as dest:
        writer = csv.DictWriter(dest, fieldnames=EXPORT_COLUMNS, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in csv.DictReader(source):
            if int(row["System"]) == UI_MAP_SYSTEM_WORLD:
                writer.writerow(row)


# Returns a function that maps a recorded zone id to the zone id it should be stored under:
#     0                                   -> 0
#     not in UiMap, or not a world map    -> 0 (stored only in zone 0)
#     type <= COLLAPSE_TO_TYPE            -> itself
#     type > COLLAPSE_TO_TYPE             -> nearest parent of type COLLAPSE_TO_TYPE, or itself if there's none
# Without a UiMap (uimap is None), zone ids are kept as they are.
def create_zone_resolver(uimap):
    cache = {}

    def resolve(zone_id):
        if uimap is None or zone_id == 0:
            return zone_id

        resolved = cache.get(zone_id)
        if resolved is not None:
            return resolved

        resolved = zone_id
        map_info = uimap.get(zone_id)
        if map_info is None or map_info["system"] != UI_MAP_SYSTEM_WORLD:
            resolved = 0
        elif map_info["type"] > COLLAPSE_TO_TYPE:
            curr_info = map_info
            depth = 0
            while depth < MAX_CHAIN_DEPTH:
                parent_id = curr_info["parent"]
                curr_info = uimap.get(parent_id) if parent_id else None
                if curr_info is None or curr_info["type"] < COLLAPSE_TO_TYPE:
                    break
                if curr_info["type"] == COLLAPSE_TO_TYPE:
                    resolved = parent_id
                    break
                depth += 1

        cache[zone_id] = resolved
        return resolved

    return resolve


# Returns a function that gives the set of parent map ids of a zone id (all the way up), or None when
# that's unknown (no UiMap, or zone id not in it).
def create_zone_ancestors(uimap):
    cache = {}

    def ancestors(zone_id):
        if uimap is None or zone_id not in uimap:
            return None

        result = cache.get(zone_id)
        if result is not None:
            return result

        result = set()
        parent_id = uimap[zone_id]["parent"]
        depth = 0
        while parent_id and depth < MAX_CHAIN_DEPTH:
            result.add(parent_id)
            parent_info = uimap.get(parent_id)
            if parent_info is None:
                break
            parent_id = parent_info["parent"]
            depth += 1

        cache[zone_id] = result
        return result

    return ancestors
