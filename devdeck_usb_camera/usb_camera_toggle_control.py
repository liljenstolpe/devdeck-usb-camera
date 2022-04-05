import logging
import os
import requests
import watchdog.events

from devdeck_core.controls.deck_control import DeckControl

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from xdg.BaseDirectory import *

defaultIconPath = os.path.join(xdg_config_dirs[0], 'devdeck/assets')
# defaultEnabledIcon = 'cameraEnabled.png'
# defaultDisabledIcon ='cameraDisabled.png'

defaultUsbRootPath = '/sys/bus/usb'
defaultUsbDriversFamily = 'uvcvideo'

class usbCameraToggleControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

        self.usbRootPath = self.settings['usbRootPath'] or defaultUsbRootPath
        self.usbDriversFamily = self.settings['usbDriversFamily'] or defaultUsbDriversFamily
        self.cameraUsbAddress = self.settings['cameraUsbAddress']
        self.observerPath = os.path.join(self.usbRootPath, 'drivers', self.usbDriversFamily)
        self.testPath = os.path.join(self.observerPath, self.cameraUsbAddress)

    def initialize(self):
        patterns = [self.cameraUsbAddress]

        if os.path.exists(self.testPath):
            renderer(created)
        else:
            renderer(deleted)

        event_handler = MyHandler(patterns, renderer())
        
        observer = Observer()
        observer.schedule(event_handler, path=observerPath, recursive=False)


    def pressed(self):
        observerPath = self.observerPath
        testPath = self.testPath
        cameraUsbAddress = self.cameraUsbAddress
        
        if os.path.exists(testPath):
            with open(os.path.join(observerPath, 'unbind')) as unbind:
                unbind.write(cameraUsbAddress)
        else:
            with open(os.path.join(observerPath, 'bind')) as bind:
                bind.write(cameraUsbAddress)

    def renderer(state):
        context = self.deck_context()
        renderer = context.renderer()

        iconPath = self.settings['iconPath'] or defaultIconPath,
        cameraEnabledIcon = self.settings['cameraEnabledIcon'],
        cameraDisabledIcon = self.settings['cameraDisabledIcon']

        if state == 'created':
            renderer.image(os.path.join(iconPath, cameraEnabledIcon))
        elif state == 'deleted':
            renderer.image(os.path.join(iconPath, cameraDisabledIcon))
        else:
            self.__logger.err("unhandled state: %s", state)

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
    def __init__(self, patterns, renderer: callable):
        self.__logger = logging.getLogger('devdeck')
        self.renderer = renderer
        self.patterns = patterns

    def on_created(self, event):
        renderer('created')        
        self.__logger.info("camera enabled")
        
    def on_deleted(self, event):
        renderer('deleted')
        self.__logger.info("camera disabled")
        

