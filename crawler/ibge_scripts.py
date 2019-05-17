import json
import threading
import time
import sys
import os

from os import listdir
from os.path import isfile, join
from helper.Chrome import Chrome
from helper.Request import Request
from helper.Interpreter import Interpreter
from helper.Exporter import Exporter
from helper.Cities import Cities


class Scripts_RS:
    def __init__(self):
        with open('./helper/objects/rio_grande_do_sul_objects.json') as f:
            self.objects = json.load(f)

        self.cities = Cities()

    def navigate_to(self, url, title, chrome=None):
        if chrome is None:
            chrome = self.chrome

        chrome.navigate(url)
        object_found = chrome.wait_for(complex_obj=title)
        if object_found is False:
            self.navigate_to(url, title)

    def navigate_ibge_labels(self, thread_name=None, verbose=False):
        if verbose is True:
            if thread_name is None:
                print(f'openning browser')
            else:
                print(f'{thread_name}: openning browser')

        chrome = Chrome()
        chrome.set_options(False).get_driver(False)

        if verbose is True:
            if thread_name is None:
                print("waiting for flag")
            else:
                print(f'{thread_name}: waiting for flag')

        self.navigate_to(
            url=self.objects['ibge']['url'],
            title=self.objects['ibge']['bandeira'],
            chrome=chrome)

        if verbose is True:
            if thread_name is None:
                print("clicking into button")
            else:
                print(f'{thread_name}: clicking into button')

        button = False
        while button is False:
            button = chrome.wait_for(
                complex_obj=self.objects['ibge']['gerar_resumo'])
        chrome.click(complex_obj=self.objects['ibge']['gerar_resumo'])

        return chrome

    def labels_action(self, chrome, start=0, end=0, click=True, thread_name=None, verbose=False):
        if verbose is True:
            if thread_name is None:
                print("getting all labels")
            else:
                print(f'{thread_name}: getting all labels')

        elements = []
        while len(elements) == 0:
            elements = chrome.get_objects(
                complex_obj=self.objects['ibge']['labels'])

        if click is False:
            return elements

        end = len(elements) if end > len(elements) else end
        for i in range(start, end):
            if verbose is True:
                print(
                    f'{thread_name}: clicking in labels {(i + 1)} from {len(elements)}')

            elements[i].click()

        if verbose is True:
            print(f'{thread_name}: opening report')

        chrome.click(complex_obj=self.objects['ibge']['gerar_relatorio'])
        chrome.driver.switch_to.window(chrome.driver.window_handles[1])
        return chrome

    def table_crawler(self, chrome, thread_name=None, verbose=False):
        if verbose is True:
            print(f'{thread_name}: waiting on table to load')

        obj = False
        while obj is False:
            obj = chrome.wait_for(
                simple_obj=self.objects['ibge']['table']['title'])

        if verbose is True:
            print(f'{thread_name}: getting columns')

        columns_xpath = self.objects['ibge']['table']['columns']
        columns = chrome.get_objects(simple_obj=columns_xpath)
        columns_names = [name.text for name in columns]

        if verbose is True:
            print(f'{thread_name}: getting rows')

        rows_xpath = self.objects['ibge']['table']['rows']['tag']
        rows = chrome.get_objects(simple_obj=rows_xpath)

        if verbose is True:
            print(f'{thread_name}: rows retrieved {len(rows)}')

        if verbose is True:
            print(f'{thread_name}: getting information')

        information_xpath = self.objects['ibge']['table']['rows']['info']
        for i in range(len(rows)):
            if (i % 50 == 0 or i == len(rows)) and verbose is True:
                print(f'{thread_name}: {i} from {len(rows)}')
            info = rows[i].find_elements_by_xpath(information_xpath)
            name = info[0].text

            for z in range(1, len(info)):
                attribute_name = columns_names[z]

                if len(info) > len(columns_names) and z == len(info) - 2:
                    attribute = info[z+1].text
                else:
                    attribute = info[z].text

                self.cities.update_city(name, attribute_name, attribute)

                if len(info) > len(columns_names) and z == len(info) - 2:
                    break

        return chrome

    def discover_number_threads(self, verbose=False):
        chrome = self.navigate_ibge_labels(verbose)
        elements = self.labels_action(chrome, click=False, verbose=verbose)

        chrome.close()
        return len(elements)

    def create_report(self, start, end, thread_name=None, verbose=False):
        chrome = self.navigate_ibge_labels(thread_name, verbose)
        chrome = self.labels_action(
            chrome, start=start, end=end, thread_name=thread_name, verbose=verbose)
        chrome = self.table_crawler(chrome, thread_name, verbose)
        chrome.close()

    def create_folder(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except IOError as excepion:
            print('Problem creating directory: ', str(excepion))

    def info_script(self):
        start = time.time()
        options_number = self.discover_number_threads()

        threads = []
        for index, number in enumerate(range(0, options_number, 6)):
            t = threading.Thread(
                target=self.create_report,
                kwargs={
                    'start': number,
                    'end': number + 6,
                    'thread_name': index + 1,
                    'verbose': True
                })
            threads.append(t)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        path = './helper/downloaded_files/IBGE'
        self.create_folder(path)
        with open(f'{path}/ibge_cities_info.json', 'w') as json_file:
            json.dump(self.cities.cities, json_file, sort_keys=False, indent=4)

        end = time.time()
        print('time elapsed: ', end - start)

    def run(self):
        self.info_script()


script = Scripts_RS()
script.run()
