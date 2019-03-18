import json
import pyrebase
import pandas as pd
from Interpreter import Interpreter

class Exporter:
    def __init__(self):
        with open('./crawler/helper/firebase/pyrebase_config.json') as f:
            config = json.load(f)

        self.db = pyrebase.initialize_app(config).database()

    def export(self, year, data_frame):
        df_as_json = data_frame.to_json(orient='index', force_ascii=False)
        json_objects = json.loads(df_as_json)

        for key in json_objects:
            raw_value = json_objects[key]
            value = { year : raw_value }
            if self.db.child('rio_grande_do_sul').child(key).get().val() is None:
                print(f'Creating first time register for {key} on year {year}')
                self.db.child("rio_grande_do_sul").child(key).set(value)
            else:
                print(f'Updating registry {key} for year {year}')
                self.db.child("rio_grande_do_sul").child(key).update(value)
