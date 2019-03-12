import os, time, sys
import chromedriver_binary

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Chrome:

    def __init__(self):
        self.driver = None
        self.options = Options()

    def raiser(self, ex):
        raise ex

    def set_options(self, headless=True):
        self.options.headless = headless
        return self

    def wait(self, count):
        time.sleep(1)
        return count + 1

    def get_driver(self, full_screen=True):
        self.driver = webdriver.Chrome(chrome_options=self.options)
        if self.options.headless is False and full_screen is True:
            self.driver.fullscreen_window()
        return self

    def get_dict(self, **kwargs):
        kwarg = {}
        for key, value in kwargs.items():
            kwarg[key] = value
        return kwarg

    def get_object(self, count=0, raiser=False, **kwargs):

        kwarg = self.get_dict(**kwargs)

        try:
            if 'id' in kwargs:
                return self.driver.find_element_by_id(kwargs.pop('id'))
            elif 'obj_class' in kwargs:
                return self.driver.find_element_by_class_name(kwargs.pop('obj_class'))
            elif 'name' in kwargs:
                return self.driver.find_element_by_name(kwargs.pop('name'))
            elif 'xpath' in kwargs:
                return self.driver.find_element_by_xpath(kwargs.pop('xpath'))
            elif 'link_text' in kwargs:
                return self.driver.find_element_by_link_text(kwargs.pop('link_text'))
            elif 'obj' in kwargs:
                obj = kwargs.pop('obj')
                xpath = '//{tag}[text()="{text}"]'.format(tag=obj['tag'], text=obj['text'])
                return self.driver.find_element_by_xpath(xpath)
            else:
                return None
        except NoSuchElementException:
            if raiser is True:
                raise NoSuchElementException
            else:
                count = self.wait(count)
                if count is 10:
                    return False
                else:
                    return self.get_object(count, raiser, **kwarg)

    def get_objects(self, count=0, raiser=False, **kwargs):

        kwarg = self.get_dict(**kwargs)

        try:
            if 'xpath' in kwargs:
                return self.driver.find_elements_by_xpath(kwargs.pop('xpath'))
            elif 'obj' in kwargs:
                obj = kwargs.pop('obj')
                xpath = '//{tag}[contains(@href, "{text}")]'.format(tag=obj['tag'], text=obj['text'])
                return self.driver.find_elements_by_xpath(xpath)
            else:
                return None
        except NoSuchElementException:
            if raiser is True:
                raise NoSuchElementException
            else:
                count = self.wait(count)
                if count is 30:
                    return False
                else:
                    return self.get_objects(count, raiser, **kwarg)

    def navigate(self, url):
        self.driver.get(url)

    def close(self):
        try:
            self.driver.close()
        except WebDriverException:
            print('[close()] Browser already closed')

    def _click(self, obj):
        if obj.is_displayed():
            obj.click()
            return self
        else:
            return self._click(obj)

    def _clear(self, obj):
        if obj.is_displayed():
            obj.clear()
            return self
        else:
            return self._clear(obj)

    def _send_keys(self, obj, text):
        if obj.is_displayed():
            obj.send_keys(text)
            return self
        else:
            return self._send_keys(obj, text)

    def click(self, count=0, **kwargs):
        obj = self.get_object(**kwargs)
        return self._click(obj) if (obj != None) else self.raiser(NoSuchElementException)

    def send_keys(self, text, count=0, **kwargs):
        obj = self.get_object(**kwargs)
        return self._send_keys(obj, text) if (obj != None) else self.raiser(NoSuchElementException)

    def clear(self, **kwargs):
        obj = self.get_object(**kwargs)
        return self._clear(obj) if (obj != None) else self.raiser(NoSuchElementException)

    def wait_for(self, **kwargs):
        obj = self.get_object(**kwargs)
        if obj is False:
            print(f'[wait_for({kwargs})] No object found after 10 seconds.')
            return obj
        else:
            return obj

    def wait_dissolve(self, **kwargs):
        try:
            self.get_object(raiser=True, **kwargs)
            return False
        except NoSuchElementException:
            return True