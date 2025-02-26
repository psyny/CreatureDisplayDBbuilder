import pandas as pd
import glob

from Libs.Serializers.lua_to_obj import lua_to_json

# List all CSV files in the 'DBs' folder
csv_files = sorted(glob.glob('DBs/*.csv'))


json_str = lua_to_json("DBs/creatureidcollector/v2/psyny.2024.02.25.lua")
print(json_str)