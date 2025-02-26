def ccdb_to_luafile(cddb, file_path):
    with open(file_path, "w") as lua_file:
        # Write the initial Lua table structure
        lua_file.write("CreatureDisplayDBdb = {}\n")

        # Write the data field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.data = {\n")
        
        # Write each entry in creature_db
        for key, cdata in cddb["data"].items():
            idx = key
            name = '[=[' + cdata['name'] + ']=]'

            lua_file.write(f"    [{idx}] = {{\n")
            lua_file.write(f"        name = {name},\n")     

            lua_file.write(f"        zone = {{\n")
            for zone_id, zdata in cdata["zone"].items():      
                lua_file.write(f"            [{zone_id}] = {{\n")            
                lua_file.write(f"                npc_ids = {{{', '.join(map(str, zdata['nids']))}}},\n")
                lua_file.write(f"                display_ids = {{{', '.join(map(str, zdata['dids']))}}}\n")
                lua_file.write("            },\n")
            lua_file.write("        },\n")                
            lua_file.write("    },\n")
        
        # Close
        lua_file.write("}\n")

        # Write the name map field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.byname = {\n")
        
        # Write each entry in creature_db
        for key, data in cddb["byname"].items():
            idx = '[=[' + str(key) + ']=]'
            lua_file.write(f"    [ {idx} ] = {data},\n")
        
        # Close
        lua_file.write("}\n")

        # Write the nid map field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.bynid = {\n")
        
        # Write each entry in creature_db
        for key, data in cddb["bynid"].items():
            idx = key
            lua_file.write(f"    [{idx}] = {data},\n")
        
        # Close
        lua_file.write("}\n")     

        # Write the did map field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.bydid = {\n")
        
        # Write each entry in creature_db
        for key, data in cddb["bydid"].items():
            idx = key
            lua_file.write(f"    [{idx}] = {data},\n")
        
        # Close
        lua_file.write("}\n")               
