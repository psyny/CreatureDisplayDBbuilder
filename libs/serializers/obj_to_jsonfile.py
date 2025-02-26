import json

def obj_to_jsonfile(obj, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(obj, file, indent=4, ensure_ascii=False)
        return "File saved successfully."
    except Exception as e:
        return f"Error writing file: {e}"
