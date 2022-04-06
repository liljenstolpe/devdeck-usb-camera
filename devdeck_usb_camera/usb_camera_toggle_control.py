import logging
import os
import requests
import watchdog.events

from typing import Union, Callable

from devdeck_core.controls.deck_control import DeckControl

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from xdg.BaseDirectory import *

defaultIconPath = os.path.join(xdg_config_dirs[0], 'devdeck/assets')

defaultUsbRootPath = '/sys/bus/usb'
defaultUsbDriversFamily = 'uvcvideo'

class usbCameraToggleControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

        self.usbRootPath = kwargs['usbRootPath'] or defaultUsbRootPath
        self.usbDriversFamily = kwargs['usbDriversFamily'] or defaultUsbDriversFamily
        self.cameraUsbAddress = kwargs['cameraUsbAddress']
        self.iconPath = kwargs['iconPath'] or defaultIconPath
        self.cameraEnabledIcon = kwargs['cameraEnabledIcon']
        self.cameraDisabledIcon = kwargs['cameraDisabledIcon']
        self.observerPath = os.path.join(self.usbRootPath, 'drivers', self.usbDriversFamily)
        self.testPath = os.path.join(self.observerPath, self.cameraUsbAddress)

    def initialize(self):
        patterns = [self.cameraUsbAddress]
        if os.path.exists(self.testPath):
            self.render(self.cameraEnabledIcon)
        else:
            self.render(self.cameraDisabledIcon)

        event_handler = MyHandler(self.cameraEnabled, self.cameraUsbAddress)
            
        observer = Observer()
        observer.schedule(event_handler, path=self.observerPath, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            observer.stop()
        observer.join()                
                
    def cameraEnabled(self, state):
        self.state = state
        
        if self.state:
            self.render(self.cameraEnabledIcon)
            self.__logger.info("camera enabled")
        else:
            self.render(self.cameraDisabledIcon)
            self.__logger.info("camera disabled")

    def pressed(self):
        observerPath = self.observerPath
        testPath = self.testPath
        cameraUsbAddress = self.cameraUsbAddress
        
        if os.path.exists(testPath):
            with open(os.path.join(observerPath, 'unbind'), "a") as unbind:
                unbind.write(cameraUsbAddress)
        else:
            with open(os.path.join(observerPath, 'bind'), "a") as bind:
                bind.write(cameraUsbAddress)

    def render(self, icon):
        iconPath = self.iconPath
                
        with self.deck_context() as context:
            with context.renderer() as r:
                r\
                    .image(os.path.join(iconPath, icon)) \
                    .center_vertically() \
                    .center_horizontally() \
                    .height(900) \
                    .width(900) \
                    .end()

    def settings_schema(self):
        return {
            'usbRootPath': {
                'type': 'string',
                'required': False
            },
            'usbDriversFamily': {
                'type': 'string',
                'required': False
            },
            'cameraUsbAddress': {
                'type': 'string',
                'required': True
           },
            'iconPath': {
                'type': 'string',
                'required': False
            },
            'cameraEnabledIcon': {
                'type': 'string',
                'required': True
            },
            'cameraDisabledIcon': {
                'type': 'string',
                'required': True
            },
        }

class MyHandler(PatternMatchingEventHandler):
    def __init__(self, callback: Callable, cameraUsbAddress):
        self.callback = callback
        self.cameraUsbAddress = cameraUsbAddress
        super().__init__(patterns = [self.cameraUsbAddress], ignore_directories=True, case_sensitive=False)
    
    def on_created(event):
        print('created')
        self.callback(True)

    def on_deleted(event):
        print('deleted')
        self.callback(False)
        