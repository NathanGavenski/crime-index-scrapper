import json
import pyrebase
import pandas as pd

from Interpreter import Interpreter

class Exporter:
    # TODO Delete all files after it send to firebase real time database
    def __init__(self):
        with open('./crawler/helper/firebase/pyrebase_config.json') as f:
            config = json.load(f)

        self.db = pyrebase.initialize_app(config).database()
        self.cities = self.db.child('rio_grande_do_sul').get()

    def export(self, year, data_frame):
        df_as_json = data_frame.to_json(orient='index', force_ascii=False)
        json_objects = json.loads(df_as_json)

        for key in json_objects:
            raw_value = json_objects[key]
            value = { year : raw_value }
            if self.check_if_exist(key) is False:
                print(f'Creating first time register for {key} on year {year}')
                self.db.child("rio_grande_do_sul").child(key).set(value)
            else:
                print(f'Updating registry {key} for year {year}')
                self.db.child("rio_grande_do_sul").child(key).update(value)

    def check_if_exist(self, city_name):
        for city in self.cities.each():
            if city.key() == city_name:
                return True
        return False


interpreter = Interpreter()
year, data = interpreter.interpret('./crawler/helper/downloaded_files/RS/city/04154946-31164429-indicadores-criminais-ssp-por-municipio-2011-por-mes.xls')

exporter = Exporter()
exporter.export(year, data)