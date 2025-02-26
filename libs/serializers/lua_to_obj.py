import re
import json

from libs.serializers.file_to_str import file_to_str
from libs.serializers.str_to_file import str_to_file

def lua_to_obj(lua_file):
    lua_str = file_to_str(lua_file)

    # Remove variable assignment at the start
    lua_str = re.sub(r'^\w+\s*=\s*', '', lua_str.strip())   

    # Replace Lua table syntax with JSON syntax
    lua_str = re.sub(r'\["(.*?)"\]', r'"\1"', lua_str)  # Convert ["key"] to "key"
    lua_str = re.sub(r'\[(\d+)\]', r'"\1"', lua_str)  # Convert [123] to "123"

    # Match keys that have unescaped double quotes inside
    # Regex to find strings inside double quotes and escape only internal quotes
    #def escape_match(m):
    #    inner_content = m.group(1).replace('"', '\\"')  # Escape inner double quotes
    #    return f'"{inner_content}"'  # Reconstruct with outer quotes intact
    #
    #lua_str = re.sub(r'"(.*?)"', escape_match, lua_str)    

    # Delimiters
    lua_str = lua_str.replace("=", ":")  # Replace = with :
    lua_str = lua_str.replace("{", "{").replace("}", "}")  # Ensure brackets remain valid
    
    # Remove trailing commas before a closing brace or bracket
    lua_str = re.sub(r',\s*([\]}])', r'\1', lua_str)    

    # DEBUG: save to file
    #str_to_file(lua_str, "testfile.json")
    
    try:
        json_obj = json.loads(lua_str)
        #return json.dumps(json_obj, indent=4)
        return json_obj
    
    except json.JSONDecodeError as e:
        print(f"Error parsing Lua to JSON: {e}")
        return None