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
      
# start = time.time()  
# cities = Cities()
# def test(name):
#     for i in range(1000):
#         cities.update_city(name, i, i)

# t1 = threading.Thread(
#     target = test,
#     kwargs = {
#         'name': 'test1'
#     })

# t2 = threading.Thread(
#     target = test,
#     kwargs = {
#         'name': 'test2'
#     })
# t1.start()
# t2.start()
# t1.join()
# t2.join()

# end = time.time()
# print('time elapsed: ', end - start)