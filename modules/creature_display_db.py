from libs.serializers.ccdb_to_luafile import ccdb_to_luafile

# Max npc ids and max display ids kept per zone. Zone 0 has no limit.
MAX_IDS_PER_ZONE = 3

def export_luafile(raw_db, file_path, zone_ancestors = None):
     cddb = create_cddb(raw_db, zone_ancestors)
     ccdb_to_luafile(cddb, file_path)


# A zone bucket is redundant when its ids are just the first ids of zone 0, in the same order: the addon merges
# zone ids first and zone 0 after, so the result is zone 0 either way.
def is_prefix_of_zone0(zdata, zone0):
    return zdata["nids"] == zone0["nids"][:len(zdata["nids"])] and zdata["dids"] == zone0["dids"][:len(zdata["dids"])]


# Removes redundant zone buckets. A redundant bucket is only kept when one of its parent maps keeps a bucket,
# because then the parent ids would come first for that zone. zone_ancestors(zone_id) gives the parent map ids,
# or None when unknown: then any other kept bucket counts as a possible parent.
def remove_redundant_zones(entry, zone_ancestors):
    zones = entry["zone"]
    zone0 = zones[0]

    redundant = set()
    for zone_id, zdata in zones.items():
        if zone_id != 0 and is_prefix_of_zone0(zdata, zone0):
            redundant.add(zone_id)

    kept = set(zones) - redundant - {0}
    for zone_id in redundant:
        ancestors = zone_ancestors(zone_id) if zone_ancestors else None
        if ancestors is None:
            has_kept_parent = len(kept) > 0
        else:
            has_kept_parent = len(kept & ancestors) > 0

        if not has_kept_parent:
            del zones[zone_id]


def create_cddb(raw_db, zone_ancestors = None):
    next_idx = 1

    creature_data = {}
    data_by_name = {}
    data_by_nid = {}
    data_by_did = {}

    cddb = {
        "data": creature_data,
        "byname": data_by_name,
        "bynid": data_by_nid,
        "bydid": data_by_did,
    }

    def get_dids_nids_empty():
        obj = {
                    "nids": [],
                    "dids": [],
                }
        return obj

    for cname, cdata in raw_db.items():
        cur_idx = next_idx
        next_idx += 1

        entry = {
            "name": cname,
            "zone": {},
        }

        creature_data[cur_idx] = entry
        data_by_name[cname] = cur_idx

        # Every id is in zone 0 and also in the zone it was seen in, so duplicates are only removed within a zone
        for zone_id, zdata in cdata["zone"].items():
            curr_dids = set()
            curr_nids = set()

            entry_zdata = get_dids_nids_empty()
            entry["zone"][zone_id] = entry_zdata

            # Ids are added by priority, then highest id first, so the cap keeps the first ones in that order
            max_ids = None if zone_id == 0 else MAX_IDS_PER_ZONE

            for priority in range(3):
                sorted_nids = list(zdata["nids"][priority])
                sorted_nids.sort(reverse=True)    
                for nid in sorted_nids:
                    if max_ids is not None and len(entry_zdata["nids"]) >= max_ids:
                        break
                    if nid in curr_nids:
                        continue
                    curr_nids.add(nid)

                    entry_zdata["nids"].append(nid)
                    data_by_nid[nid] = cur_idx

                sorted_dids = list(zdata["dids"][priority])
                sorted_dids.sort(reverse=True)    
                for did in sorted_dids:
                    if max_ids is not None and len(entry_zdata["dids"]) >= max_ids:
                        break
                    if did in curr_dids:
                        continue
                    curr_dids.add(did)

                    entry_zdata["dids"].append(did)
                    data_by_did[did] = cur_idx

            # Zone 0 is always kept, other zones only when they have ids
            if zone_id != 0 and not entry_zdata["nids"] and not entry_zdata["dids"]:
                del entry["zone"][zone_id]

        remove_redundant_zones(entry, zone_ancestors)

    return cddb



