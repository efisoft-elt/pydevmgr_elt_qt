import fnmatch
from typing import Dict, Optional
from PyQt5 import uic
from PyQt5.QtWidgets import QFrame, QVBoxLayout
from pydevmgr_core import BaseDevice
from pydevmgr_qt.api import Connector, QtDevice, find_ui

class DefaultContainerWidget(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ly_devices = QVBoxLayout()
        self.setLayout(self.ly_devices)

class QtDeviceView(QtDevice):
    class Config:
        ui_file: Optional[str] = None 
        device: str = "*"

    def set_view(self, devices: Dict[str, BaseDevice], connection: Connector):
        container = self.get_container() 
        devices = self.filter_devices(devices)
        
    def filter_devices(self, devices: Dict[str, BaseDevice])-> Dict[str, BaseDevice]:
        return {name:devices[name] for name in fnmatch.filter(devices, self.device)}

    def get_container(self):
        if self.ui_file is None: 
            container = DefaultContainerWidget()
        else:
            ui_file = find_ui(self.ui_file)
            container = QFrame()
            uic.loadUi(ui_file, self) 
        return container 
