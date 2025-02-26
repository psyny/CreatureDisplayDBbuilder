def str_to_file(data_str, file_path):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(data_str)
        return "File saved successfully."
    except Exception as e:
        return f"Error writing file: {e}"
