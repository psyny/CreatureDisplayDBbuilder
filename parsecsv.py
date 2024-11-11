import pandas as pd
import glob

# List all CSV files in the 'DBs' folder
csv_files = sorted(glob.glob('DBs/*.csv'))

# Open the last CSV file into a DataFrame
df = None
if csv_files:  # Check if the list is not empty
    df = pd.read_csv(csv_files[-1])

# Initialize the dictionary
creature_db = {
    "data": {},
    "byname": {},
    "byid": {},
}
nextIdx = 1

# Iterate over each row in the DataFrame
for _, row in df.iterrows():
    # Get the primary name and alt name
    name = row["Name_lang"]
    alt_name = row["NameAlt_lang"]
    npc_id = row["ID"]
    
    # Display IDs from DisplayID_0, DisplayID_1, DisplayID_2, DisplayID_3 columns
    display_ids = {row["DisplayID_0"], row["DisplayID_1"], row["DisplayID_2"], row["DisplayID_3"]}

    # Helper function to add a name to the creature_db dictionary
    def add_to_creature_db(name_key):      
        if type(name_key) != type('xxx'):
            return  
        if not name_key or name_key == "":
            return
        
        global nextIdx
                
        # Get or create creature data
        idx = 0
        if name_key not in creature_db["byname"]:
            # Idx by name
            idx = nextIdx
            nextIdx += 1

            creatureData = {
                "name": name,
                "npc_ids": set(),
                "display_ids": set()
            }

            creature_db["data"][idx] = creatureData
            creature_db["byname"][name_key] = idx

        else:
            # Get current idx of name
            idx = creature_db["byname"][name_key]
        
        creatureData = creature_db["data"][idx]

        # Update indexing by npc_id
        creature_db["byid"][npc_id] = idx

        # Add npc_id to the npc_ids set
        creatureData["npc_ids"].add(npc_id)

        # Add each display_id to the display_ids set
        creatureData["display_ids"].update(display_ids)

    # Add for both name and alt name
    add_to_creature_db(name)
    add_to_creature_db(alt_name)

# Now, get rid of the sets and turn into list
for name, data in creature_db["data"].items():
    # Convert sets to lists
    if 0 in data["npc_ids"]:
        data["npc_ids"].remove(0)
    data["npc_ids"] = list(data["npc_ids"])
    data["npc_ids"].sort(reverse=True)

    if 0 in data["display_ids"]:
        data["display_ids"].remove(0)
    data["display_ids"] = list(data["display_ids"])
    data["display_ids"].sort(reverse=True)    

# save to lua
# Function to write creature_db to Lua file
def write_to_lua(creature_db, file_path="CreatureDisplayDBdb.lua"):
    with open(file_path, "w") as lua_file:
        # Write the initial Lua table structure
        lua_file.write("CreatureDisplayDBdb = {}\n")

        # Write the data field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.data = {\n")
        
        # Write each entry in creature_db
        for key, data in creature_db["data"].items():
            idx = key
            name = '[=[' + data['name'] + ']=]'

            lua_file.write(f"    [{idx}] = {{\n")
            lua_file.write(f"        name = {name},\n")
            lua_file.write(f"        npc_ids = {{{', '.join(map(str, data['npc_ids']))}}},\n")
            lua_file.write(f"        display_ids = {{{', '.join(map(str, data['display_ids']))}}}\n")
            lua_file.write("    },\n")
        
        # Close
        lua_file.write("}\n")

        # Write the name map field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.byname = {\n")
        
        # Write each entry in creature_db
        for key, data in creature_db["byname"].items():
            idx = '[=[' + str(key) + ']=]'
            lua_file.write(f"    [ {idx} ] = {data},\n")
        
        # Close
        lua_file.write("}\n")

        # Write the id map field ---------------------------------
        lua_file.write("CreatureDisplayDBdb.byid = {\n")
        
        # Write each entry in creature_db
        for key, data in creature_db["byid"].items():
            idx = key
            lua_file.write(f"    [{idx}] = {data},\n")
        
        # Close
        lua_file.write("}\n")        


# Usage
write_to_lua(creature_db)