import logging
import os
import requests
import usb.core
import time
import threading

from devdeck_core.controls.deck_control import DeckControl

from xdg.BaseDirectory import *

defaultIconPath = os.path.join(xdg_config_dirs[0], 'devdeck/assets')

class usbCameraToggleControl(DeckControl):

    def __init__(self, key_no, **kwargs):
        self.__logger = logging.getLogger('devdeck')
        super().__init__(key_no, **kwargs)

        self.iconPath = kwargs['iconPath'] or defaultIconPath
        self.cameraEnabledIcon = kwargs['cameraEnabledIcon']
        self.cameraDisabledIcon = kwargs['cameraDisabledIcon']
        self.cameraVdi = kwargs['cameraVdi']
        self.cameraPdi = kwargs['cameraPdi']

        self.cam = usb.core.find(idVendor=self.cameraVdi,
         idProduct=self.cameraPdi)      

    def initialize(self):
        
        watcherThread = threading.Thread(target=self.watcher)
        watcherThread.start()

    def watcher(self):
        self.state = None

        while True:
            if self.state != self.cam.is_kernel_driver_active(0):
                self.state = self.cam.is_kernel_driver_active(0)
                self.displayChange(self.state)
            time.sleep(0.1)
        self.__logger.error("We should never exit the thread - oops!")
        exit(1)

    def displayChange(self, state):
        self.state = state
        
        if self.state:
            self.render(self.cameraEnabledIcon)
            self.__logger.info("camera enabled")
        else:
            self.render(self.cameraDisabledIcon)
            self.__logger.info("camera disabled")

    def render(self, icon):
        iconPath = self.iconPath
                
        with self.deck_context() as context:
            with context.renderer() as r:
                r\
                    .image(os.path.join(iconPath, icon)) \
                    .center_vertically() \
                    .center_horizontally() \
                    .height(300) \
                    .width(300) \
                    .end()

    def pressed(self):
                
        if not self.cam.is_kernel_driver_active(0):
            self.cam.attach_kernel_driver(0)
        else:
            self.cam.detach_kernel_driver(0)
            
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
            'cameraVdi': {
                'type': 'integer',
                'required': True
            },
            'cameraPdi': {
                'type': 'integer',
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