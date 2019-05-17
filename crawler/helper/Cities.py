import threading, time, json

class Cities:
    
    def __init__(self):
        self.cities = {}
        self.wait = False
        
    def __add_city(self, city_name):
        self.wait = True
        self.cities[city_name] = {}
        self.wait = False
        
    def update_city(self, city_name, attribute_name, attribute):
        try:
            self.cities[city_name][attribute_name] = attribute
            return True
        except KeyError:
            while self.wait is True: pass
            self.__add_city(city_name)
            return self.update_city(city_name, attribute_name, attribute)
        except:
            return False
        
    def to_string(self):
        return json.dumps(self.cities, 
                          ensure_ascii=False, 
                          sort_keys=True,
                          indent=2)