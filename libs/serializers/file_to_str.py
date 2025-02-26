def file_to_str(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lua_data = file.read()
        return lua_data
    except FileNotFoundError:
        return "Error: File not found."
    except Exception as e:
        return f"Error reading file: {e}"