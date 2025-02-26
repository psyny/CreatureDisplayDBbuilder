from libs.serializers.ccdb_to_luafile import ccdb_to_luafile

def export_luafile(raw_db, file_path):
     cddb = create_cddb(raw_db)
     ccdb_to_luafile(cddb, file_path)


def create_cddb(raw_db):
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

        curr_dids = set()
        curr_nids = set()

        for zone_id, zdata in cdata["zone"].items():
            entry_zdata = get_dids_nids_empty()
            entry["zone"][zone_id] = entry_zdata
            for priority in range(3):
                sorted_nids = list(zdata["nids"][priority])
                sorted_nids.sort(reverse=True)    
                for nid in sorted_nids:
                    if nid in curr_nids:
                        continue
                    curr_nids.add(nid)

                    entry_zdata["nids"].append(nid)
                    data_by_nid[nid] = cur_idx

                sorted_dids = list(zdata["dids"][priority])
                sorted_dids.sort(reverse=True)    
                for did in sorted_dids:
                    if did in curr_dids:
                        continue
                    curr_dids.add(did)

                    entry_zdata["dids"].append(did)
                    data_by_did[did] = cur_idx                    

    return cddb



