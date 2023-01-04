
from dataclasses import dataclass
from enum import Enum
from typing import Tuple
from pydevmgr_core_qt import (
        Action, ActionMap, 
        QtChangeStyleContainerFeedback,    
        QtBaseDevice, get_connector_class, get_setter_class, get_getter_class,  
    )
        
from PyQt5 import uic
from PyQt5.QtWidgets import QCheckBox, QComboBox, QFrame, QLabel, QPushButton, QLineEdit
from pydevmgr_elt.base.eltdevice import EltDevice

from pydevmgr_elt_qt.helpers import CodeTextGroupSetter

Device = EltDevice

class Widget(QFrame):
    ...

class Proc:
    check_connector =  get_connector_class(QCheckBox, Action)()
    menu_connector = get_connector_class(QComboBox, ActionMap)() 
    button_connector = get_connector_class(QPushButton, Action)()  
    float_getter = get_getter_class(QLineEdit, float)(feedback=QtChangeStyleContainerFeedback())
    float_setter = get_setter_class(QLabel, float)(format="%.2f")
    code_text_setter = CodeTextGroupSetter()
    text_setter  = get_setter_class(QLabel, str)()
    text_getter  = get_getter_class(QLabel, str)()

    
class Data(QtBaseDevice.Monitor.Data):
    ... 

@dataclass
class Args:
    ...

@dataclass
class Actions:
   ... 

##################################################################

def update_data(w: Widget, data: Data):
    ...

def set_widget(widget: Widget, device: Device):
   ... 

def set_args(args: Args, widget: Widget) -> None:
    ...

def set_actions(actions: Actions, widget, device)-> None:
    ...

def connect_action(widget: Widget, actions: Actions) -> None:
    widget.device_actions = actions # need to be saved (weakref) 


def disconnect_action(widget: Widget) -> None:
    ...

       
##################################################################


class QtBase(QtBaseDevice):
    Proc = Proc
    Widget = Widget

    class Monitor(QtBaseDevice.Monitor):
        Data = Data
        _update_data = staticmethod(update_data)        
        
         
        def update(self, widget: QFrame , data) -> None:
            """ update the ui from the data structure """
            super().update(widget, data)
            self._update_data(widget, data)

    class Connector(QtBaseDevice.Connector):  
        Args = Args
        Actions = Actions
        _set_widget        = staticmethod(set_widget)
        _set_args          = staticmethod(set_args)
        _set_actions       = staticmethod(set_actions)
        _connect_action    = staticmethod(connect_action)
        _disconnect_action = staticmethod(disconnect_action)
        
        
        def connect(self, widget: Widget, device: Device)-> None:
            args = self.Args()
            actions = self.Actions() 
            
            self._set_widget(widget, device)
            self._set_args(args, widget)
            self._set_actions(actions, device, args)
            self._connect_action( widget, actions)
        
        def disconnect(self, widget: Widget)-> None:
            self._disconnect_action(widget)     
 
