# CreatureDisplayDBbuilder
Database Builder for my World Of Warcraft Addon Creature Display DB

## Setup

```
python -m pip install -r requirements.txt
```

## Running

```
python app.py            # builds every flavor (retail, forever)
python app.py retail     # builds only one flavor
```

Sources are read from `dbs/<flavor>/` and written to `output/CreatureDisplayDB_<flavor>_db_general.lua`.
