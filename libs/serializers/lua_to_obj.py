try:
    import lupa.lua54 as lupa
except ImportError:
    import lupa

from libs.serializers.file_to_str import file_to_str

_lua = lupa.LuaRuntime()

# Runs a Lua chunk inside an empty environment and returns that environment,
# so the globals the file defines (e.g. a SavedVariables table) can be read back
# without the file touching the real Lua globals. Works on Lua 5.1/LuaJIT (setfenv) and 5.2+ (load with env).
_run_sandboxed = _lua.eval("""
function(src, chunkname)
    local env = {}
    local chunk, err
    if setfenv then
        chunk, err = loadstring(src, chunkname)
        if chunk then
            setfenv(chunk, env)
        end
    else
        chunk, err = load(src, chunkname, "t", env)
    end
    if not chunk then
        return nil, err
    end

    local ok, runErr = pcall(chunk)
    if not ok then
        return nil, runErr
    end

    return env, nil
end
""")


# Converts Lua tables into python dicts, recursively.
# Tables always become dicts (never lists): Lua can't tell { [1] = 1 } from { 1 }, and the
# CreatureIdCollector sets use npc ids as keys. Integer keys stay integers.
def _to_py(value):
    if lupa.lua_type(value) == "table":
        return {key: _to_py(sub_value) for key, sub_value in value.items()}
    return value


# Loads a Lua file (e.g. a WoW SavedVariables file) and returns the table assigned to var_name.
# If var_name is None, the file must define exactly one global, and that one is returned.
# Returns None on error.
def lua_to_obj(lua_file, var_name = None):
    lua_str = file_to_str(lua_file)

    env, err = _run_sandboxed(lua_str, "@" + lua_file)
    if env is None:
        print(f"Error parsing Lua file {lua_file}: {err}")
        return None

    globals_defined = _to_py(env)

    if var_name is not None:
        if var_name not in globals_defined:
            print(f"Error parsing Lua file {lua_file}: global '{var_name}' not found")
            return None
        return globals_defined[var_name]

    if len(globals_defined) != 1:
        print(f"Error parsing Lua file {lua_file}: expected one global, found {len(globals_defined)} ({', '.join(map(str, globals_defined))})")
        return None

    return next(iter(globals_defined.values()))
