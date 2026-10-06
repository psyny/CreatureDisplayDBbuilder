from libs.serializers.ccdb_to_luafile import ccdb_to_luafile

# Max npc ids and max display ids kept per zone.
MAX_IDS_PER_ZONE = 3
# Zone 0 keeps every base id (game Creature table) plus up to this many npc ids and display ids from the other sources.
MAX_NON_BASE_IDS_ZONE0 = 10

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

            # Ids are added by priority, then highest id first, so the cap keeps the first ones in that order.
            # Zone 0 caps only the non base ids, other zones cap all ids.
            if zone_id == 0:
                max_ids = MAX_NON_BASE_IDS_ZONE0
                base_nids = zdata["base_nids"]
                base_dids = zdata["base_dids"]
            else:
                max_ids = MAX_IDS_PER_ZONE
                base_nids = set()
                base_dids = set()
            capped_nids_qty = 0
            capped_dids_qty = 0

            for priority in range(3):
                sorted_nids = list(zdata["nids"][priority])
                sorted_nids.sort(reverse=True)    
                for nid in sorted_nids:
                    if nid in curr_nids:
                        continue
                    if nid not in base_nids:
                        if capped_nids_qty >= max_ids:
                            continue
                        capped_nids_qty += 1
                    curr_nids.add(nid)

                    entry_zdata["nids"].append(nid)
                    data_by_nid[nid] = cur_idx

                sorted_dids = list(zdata["dids"][priority])
                sorted_dids.sort(reverse=True)    
                for did in sorted_dids:
                    if did in curr_dids:
                        continue
                    if did not in base_dids:
                        if capped_dids_qty >= max_ids:
                            continue
                        capped_dids_qty += 1
                    curr_dids.add(did)

                    entry_zdata["dids"].append(did)
                    data_by_did[did] = cur_idx

            # Zone 0 is always kept, other zones only when they have ids
            if zone_id != 0 and not entry_zdata["nids"] and not entry_zdata["dids"]:
                del entry["zone"][zone_id]

        remove_redundant_zones(entry, zone_ancestors)

    return cddb



