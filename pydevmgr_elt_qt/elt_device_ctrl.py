from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from pydantic.fields import Field
from pydevmgr_core_qt import (Action, ActionMap, 
        QtTextFeedback, QtFloatSetter,  QtTextSetter,
        QtChangeStyleContainerFeedback,  QtFloatGetter,  
        QtBaseDevice, get_connector_class, QtDataSetter, QtInterface
        )
        
from PyQt5 import uic
from PyQt5.QtWidgets import QCheckBox, QComboBox, QFrame, QLabel, QPushButton
from pydevmgr_core_ui import feedback

from pydevmgr_elt_qt.helpers import CodeTextGroupSetter
from .io import find_ui
from pydevmgr_core import NodeVar
from pydantic import BaseModel 


class DeviceCtrlWidget(QFrame):
    state: QLabel 
    substate: QLabel
    error_txt: QLabel
    state_action: QComboBox
    rpc_feedback: QLabel

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(find_ui('device_ctrl_frame.ui'), self) 

class Proc:
    check_connector =  get_connector_class(QCheckBox, Action)()
    menu_connector = get_connector_class(QComboBox, ActionMap)() 
    button_connector = get_connector_class(QPushButton, Action)()  
    float_getter = QtFloatGetter(feedback=QtChangeStyleContainerFeedback())
    float_setter = QtFloatSetter(format="%.2f")
    code_text_setter = CodeTextGroupSetter()

    
NT, D = NodeVar[Tuple[int,str,str]],  (0,'','')
class DeviceCtrlData(QtBaseDevice.Monitor.Data):
    class Stat(BaseModel):
        state_info: NT    = Field(D, ui_interface=QtInterface("state", Proc.code_text_setter))
        substate_info: NT = Field(D, ui_interface=QtInterface("substate", Proc.code_text_setter))
        error_info: NT    = Field(D, ui_interface=QtInterface("error_txt", Proc.code_text_setter))
 
    stat: Stat = Stat()
    is_ignored: NodeVar[bool] = False
    name: str = "" # device name    
del NT, D


class DeviceCtrlSetter:
    def set(self, w, data):
        s = data.stat 
        Proc.code_text_setter.set( w.state, s.state_info)
        Proc.code_text_setter.set( w.substate, s.substate_info)
        Proc.code_text_setter.set( w.error_txt, s.error_info)



@dataclass
class DeviceCtrlActions:
    command: ActionMap
    check: Action


def set_device_ctrl_widget(widget):
    wa = widget.state_action
    wa.clear()
    wa.addItems( ["", "INIT", "ENABLE", "DISABLE", "RESET"] )


def device_ctrl_actions(widget, device)-> DeviceCtrlActions:
    feedback = QtTextFeedback( widget.rpc_feedback )
    reset = lambda: widget.state_action.setCurrentIndex(0)
    
    command = ActionMap(
            dict(
                INIT    = Action(device.init,    [], feedback), 
                ENABLE  = Action(device.enable,  [], feedback),
                DISABLE = Action(device.disable, [], feedback), 
                RESET   = Action(device.reset,   [], feedback)
            ), after=reset)
    
    return DeviceCtrlActions(
            command = command, 
            check = Action(device.is_ignored.set, [lambda: not widget.check.isChecked()]) 
        )


def device_ctrl_connect(widget, device):
    actions = device_ctrl_actions(widget, device)
    Proc.menu_connector.connect( widget.state_action, actions.command)
    Proc.check_connector.connect( widget.check, actions.check)
    widget.device_actions = actions     

def device_ctrl_disconnect(widget):
    Proc.menu_connector.disconnect(widget.state_action)
    Proc.check_connector.disconnect(widget.check)
        


class EltDeviceCtrl(QtBaseDevice):
    Proc = Proc
    Widget = DeviceCtrlWidget
    
    def __init__(self, device):
        super().__init__(device)
        self.link.data.name = device.name
    

    class Monitor(QtBaseDevice.Monitor):
        Data = DeviceCtrlData
        DataSetter = DeviceCtrlSetter
        data_setter = DataSetter()
        
        
        show_ignore_check_box: bool = True 
 
        def start(self, widget, data):
            widget.name.setText(str(data.name)) 
        
        def update(self, widget: QFrame , data) -> None:
            """ update the ui from the data structure """
            super().update(widget, data)
            
            if self.show_ignore_check_box:
                if widget.check.isChecked() == data.is_ignored:             
                    widget.check.setChecked(not data.is_ignored)    
            
            # all the data already linked to a field will be updated here 
            self.data_setter.set(widget, data)


    class Connector(QtBaseDevice.Connector):    
         
        def connect(self, widget,  device):
            device_ctrl_connect(widget, device)
        
        def disconnect(self, widget):
            device_ctrl_disconnect(widget)

