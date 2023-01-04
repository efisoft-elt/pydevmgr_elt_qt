from dataclasses import dataclass
from enum import IntEnum, Enum
from typing import Callable
from PyQt5.QtWidgets import QComboBox, QFrame, QLabel, QLineEdit, QPushButton
from pydevmgr_core_ui.feedback import BaseFeedback
from pydevmgr_core_ui.getter import get_getter_class

from pydevmgr_elt import Shutter
from PyQt5 import uic, QtWidgets
from pydevmgr_elt_qt.io import find_ui
from pydevmgr_core_qt import  ( QtTextFeedback,  Action,  record_qt) 
from pydevmgr_core import NodeVar 
import pydevmgr_elt_qt.device.ctrl as base 

Base = base.EltDeviceCtrl

Device = Shutter


class Widget(base.Widget):
    #  e.g.  pos_actual: QLabel
    
    def __init__(self,*args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        uic.loadUi(find_ui('shutter_ctrl_frame.ui'), self) 

Proc = base.Proc
Data = base.Data 
Args = base.Args 

@dataclass
class Actions(base.Actions):
    # e.g. stop: Action
    close: Action = None
    open: Action = None

##############################################################

set_widget = base.set_widget
update_data = base.update_data
set_args = base.set_args

def set_actions(actions: Actions, device: Device, args: Args)-> Actions:
    base.set_actions(actions, device, args)
    feedback = args.feedback
    actions.close = Action(device.close, [], feedback) 
    actions.open = Action(device.open, [], feedback)


def connect_action(widget: Widget, actions: Actions) -> None:
    base.connect_action(widget, actions)
    Proc.button_connector.connect( widget.close, actions.close)
    Proc.button_connector.connect( widget.open, actions.open)

def disconnect_action(widget: Widget) -> None:
    base.disconnect_action(widget)
    Proc.button_connector.disconnect( widget.close)
    Proc.button_connector.disconnect( widget.open)
   

######################################################################

@record_qt(Shutter, "ctrl")
class ShutterCtrl(Base):
    Widget = Widget
        
    class Monitor(Base.Monitor):
        Data = Data
        _update_data = staticmethod(update_data)

    class Connector(Base.Connector):
        Args = Args
        Actions = Actions
       
        _set_widget        = staticmethod(set_widget)
        _set_args          = staticmethod(set_args)
        _set_actions       = staticmethod(set_actions)
        _connect_action    = staticmethod(connect_action)
        _disconnect_action = staticmethod(disconnect_action)
