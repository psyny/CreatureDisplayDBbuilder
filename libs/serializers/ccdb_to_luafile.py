def _lua_long_string(value):
    return '[=[' + str(value) + ']=]'


def _lua_id_list(ids):
    return "{" + ",".join(map(str, ids)) + "}"


# Empty id lists are not written (npc_ids / display_ids are nil in Lua), CreatureDisplayDB.lua handles that.
# Saves one table per empty list.
def _lua_zone_data(zdata):
    fields = []
    if zdata["nids"]:
        fields.append("npc_ids=" + _lua_id_list(zdata["nids"]))
    if zdata["dids"]:
        fields.append("display_ids=" + _lua_id_list(zdata["dids"]))
    return "{" + ",".join(fields) + "}"


# Writes the DB compactly: one entry per line, no indentation. Whitespace doesn't change what the
# addon loads, it only makes the file bigger and slower to parse.
def ccdb_to_luafile(cddb, file_path):
    with open(file_path, "w", encoding="utf-8", newline="\n") as lua_file:
        # Write the initial Lua table structure
        lua_file.write("CreatureDisplayDBdb = {}\n")

        # Write the data field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.data = {\n")

        # Write each entry in creature_db
        for idx, cdata in cddb["data"].items():
            zones = ",".join(
                f"[{zone_id}]={_lua_zone_data(zdata)}"
                for zone_id, zdata in cdata["zone"].items()
            )
            lua_file.write(f"[{idx}]={{name={_lua_long_string(cdata['name'])},zone={{{zones}}}}},\n")

        # Close
        lua_file.write("}\n")

        # Write the name map field ---------------------------------
        # The space in "[ [=[" is needed: "[[=[" would start a long string
        lua_file.write("CreatureDisplayDBdb.byname = {\n")
        for name, idx in cddb["byname"].items():
            lua_file.write(f"[ {_lua_long_string(name)} ]={idx},\n")
        lua_file.write("}\n")

        # Write the nid map field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.bynid = {\n")
        for nid, idx in cddb["bynid"].items():
            lua_file.write(f"[{nid}]={idx},\n")
        lua_file.write("}\n")

        # Write the did map field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.bydid = {\n")
        for did, idx in cddb["bydid"].items():
            lua_file.write(f"[{did}]={idx},\n")
        lua_file.write("}\n")
