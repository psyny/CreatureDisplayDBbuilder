import pandas as pd

# Works for the creature csv only
# got from https://wago.tools/db2/Creature?build=11.1.0.59347

def wagocsv_to_obj(file_path):
    # Open the last CSV file into a DataFrame
    df = pd.read_csv(file_path)

    db = []

    # Iterate over each row in the DataFrame
    for _, row in df.iterrows():
        # Get the primary name and alt name
        name = row["Name_lang"]
        alt_name = row["NameAlt_lang"]
        npc_ids = [row["ID"],]
        display_ids = [row["DisplayID_0"], row["DisplayID_1"], row["DisplayID_2"], row["DisplayID_3"]]

        if type(name) == str and len(name) > 0:
            db.append(
                {
                    "name": name,
                    "nids": npc_ids,
                    "dids": display_ids,
                }
            )

        if type(alt_name) == str and len(alt_name) > 0:
            db.append(
                {
                    "name": alt_name,
                    "nids": npc_ids,
                    "dids": display_ids,
                }
            )        

    return db