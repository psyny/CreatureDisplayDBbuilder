def _lua_long_string(value):
    return '[=[' + str(value) + ']=]'


# Each creature record is written as one string, the addon turns it into a table only when it's looked up
# (see GetCreatureEntry in CreatureDisplayDB.lua). A string per record instead of 4-5 tables per record makes
# the DB much smaller in memory and faster to load. Format:
#     name<TAB>zoneId:npcIds:displayIds;zoneId:npcIds:displayIds;...
# ids are comma separated, an empty list is an empty field. Ex: "Infernal\t0:137324,108452:87778,72978"
RECORD_NAME_SEPARATOR = "\t"
RECORD_ZONE_SEPARATOR = ";"
RECORD_FIELD_SEPARATOR = ":"
RECORD_ID_SEPARATOR = ","


def _record_string(cdata):
    name = cdata["name"]
    if RECORD_NAME_SEPARATOR in name or "]=]" in name:
        raise ValueError("Creature name can't be written in a DB record: " + repr(name))

    zones = RECORD_ZONE_SEPARATOR.join(
        RECORD_FIELD_SEPARATOR.join((
            str(zone_id),
            RECORD_ID_SEPARATOR.join(map(str, zdata["nids"])),
            RECORD_ID_SEPARATOR.join(map(str, zdata["dids"])),
        ))
        for zone_id, zdata in cdata["zone"].items()
    )
    return name + RECORD_NAME_SEPARATOR + zones


# WoW's Lua 5.1 allows at most 262143 distinct constants (numbers and strings) per function, and a file is one
# function. The DB has more than that, so each table is filled by several functions, each one under this limit:
#     CreatureDisplayDBdb.bynid = {}
#     do local function f() local t = CreatureDisplayDBdb.bynid
#     t[1]=1
#     ...
#     end f() end
# The tables the addon gets are the same as with a single table constructor.
MAX_CONSTANTS_PER_FUNCTION = 100000


class _ChunkedTableWriter:
    def __init__(self, lua_file, table_path):
        self.lua_file = lua_file
        self.table_path = table_path
        self.constants = None
        lua_file.write(f"{table_path} = {{}}\n")

    # constants: every distinct number and string the statement uses
    def add(self, statement, constants):
        # Only the new constants are counted: a union with the whole set on every statement is too slow
        if self.constants is not None and len(self.constants) + len(constants - self.constants) > MAX_CONSTANTS_PER_FUNCTION:
            self.close()
        if self.constants is None:
            self.lua_file.write(f"do local function f() local t = {self.table_path}\n")
            # The global table name and its field name are constants of the function too
            self.constants = set(self.table_path.split("."))
        self.constants |= constants
        self.lua_file.write(statement + "\n")

    def close(self):
        if self.constants is not None:
            self.lua_file.write("end f() end\n")
            self.constants = None


# Writes the DB compactly: one entry per line, no indentation. Whitespace doesn't change what the
# addon loads, it only makes the file bigger and slower to parse.
def ccdb_to_luafile(cddb, file_path):
    with open(file_path, "w", encoding="utf-8", newline="\n") as lua_file:
        # Write the initial Lua table structure
        lua_file.write("CreatureDisplayDBdb = {}\n")

        # Write the data field ---------------------------------
        writer = _ChunkedTableWriter(lua_file, "CreatureDisplayDBdb.data")
        for idx, cdata in cddb["data"].items():
            record = _record_string(cdata)
            writer.add(f"t[{idx}]={_lua_long_string(record)}", {idx, record})
        writer.close()

        # Write the name map field ---------------------------------
        # The space in "[ [=[" is needed: "[[=[" would start a long string
        writer = _ChunkedTableWriter(lua_file, "CreatureDisplayDBdb.byname")
        for name, idx in cddb["byname"].items():
            writer.add(f"t[ {_lua_long_string(name)} ]={idx}", {name, idx})
        writer.close()

        # Write the nid map field ---------------------------------
        writer = _ChunkedTableWriter(lua_file, "CreatureDisplayDBdb.bynid")
        for nid, idx in cddb["bynid"].items():
            writer.add(f"t[{nid}]={idx}", {nid, idx})
        writer.close()

        # Write the did map field ---------------------------------
        writer = _ChunkedTableWriter(lua_file, "CreatureDisplayDBdb.bydid")
        for did, idx in cddb["bydid"].items():
            writer.add(f"t[{did}]={idx}", {did, idx})
        writer.close()
