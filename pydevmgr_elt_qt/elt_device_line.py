from typing import Tuple
from PyQt5.QtWidgets import QCheckBox, QComboBox, QFrame, QLabel
from pydantic.fields import Field
from pydantic.main import BaseModel
from pydevmgr_core import NodeVar
from pydevmgr_core_qt import (QtFloatSetter, QtTextSetter,  
                               Action, ActionMap, QtBaseDevice, 
                               QtChangeStyleContainerFeedback, QtFloatGetter,
                               get_connector_class
                            )
from pydevmgr_core_ui.setter import get_setter_class
from pydevmgr_elt_qt.helpers import CodeTextGroupSetter
from dataclasses import dataclass


@dataclass
class MenuErrorFeedback:
    widget: QComboBox
    def error(self,  err: Exception):
        self.widget.setItemText(0, "!!ERROR!!")
    def clear(self,  msg: str):
        self.widget.setItemText(0, "")


class DeviceLinewidget(QFrame):
    substate: QLabel
    state_action: QComboBox
    check: QCheckBox


class Proc:
    code_text_group = CodeTextGroupSetter()
    float_setter = QtFloatSetter()
    text_setter  = QtTextSetter()
    check_connector =  get_connector_class(QCheckBox, Action)()
    menu_connector = get_connector_class(QComboBox, ActionMap)() 
    float_getter = QtFloatGetter(feedback=QtChangeStyleContainerFeedback())


class DeviceLineData(QtBaseDevice.Monitor.Data):
    class Stat(BaseModel):
        substate_info: NodeVar[Tuple] = (0,'','')

    stat: Stat  = Stat()
    is_ignored: NodeVar[bool] = False
    name: str = "" # device name  

class DeviceLineSetter:
    def set(self, w, data):
        Proc.code_text_group.set(w.substate, data.stat.substate_info)   


def set_device_line_widget( widget):
    wa = widget.state_action
    wa.clear()
    wa.addItems( ["", "INIT", "ENABLE", "DISABLE", "RESET"] )



@dataclass
class DeviceLineActions:
    command: ActionMap
    check: Action


def device_line_actions(widget, device)-> DeviceLineActions:
    reset = lambda: widget.state_action.setCurrentIndex(0)
    feedback = MenuErrorFeedback(widget.state_action)
    

    command_actions = dict(
        INIT = Action(device.init,       [], feedback), 
        ENABLE = Action(device.enable,   [], feedback), 
        DISABLE = Action(device.disable, [], feedback), 
        RESET = Action(device.reset,     [], feedback)
    )
    command = ActionMap(command_actions, after=reset)

    return DeviceLineActions(
            command = command, 
            check = Action(device.is_ignored.set, [lambda: not widget.check.isChecked()]) 
    )

def device_line_connect(widget, device):
    set_device_line_widget(widget)

    actions = device_line_actions(widget, device)
    
    Proc.menu_connector.connect( widget.state_action, actions.command)
    Proc.check_connector.connect( widget.check, actions.check)
    widget.device_line_actions = actions     

def device_line_disconnect(widget):
    Proc.menu_connector.disconnect(widget.state_action)
    Proc.check_connector.disconnect(widget.check)


class EltDeviceLine(QtBaseDevice):
    def __init__(self, device):
        super().__init__(device)
        self.link.data.name = device.name
    Proc = Proc    
    Widget = DeviceLinewidget

    class Monitor(QtBaseDevice.Monitor):
        Data = DeviceLineData
        DataSetter= DeviceLineSetter
        data_setter = DataSetter()
        show_ignore_check_box = True
        
        def start(self, widget, data):
            widget.name.setText(str(data.name)) 

        def update(self, widget, data):
            self.data_setter.set(widget, data)
            if self.show_ignore_check_box:
                if widget.check.isChecked() == data.is_ignored:             
                    widget.check.setChecked(not data.is_ignored)    
        

    class Connector(QtBaseDevice.Connector):
            
        def connect(self, widget, device):
            device_line_connect( widget, device)
   
        def disconnect(self, widget):
            device_line_disconnect(widget)
